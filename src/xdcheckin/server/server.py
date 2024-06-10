# -*- coding: utf-8 -*-

__all__ = ("server_routes", "create_server", "start_server")

from asyncio import create_task as _create_task, sleep as _sleep
from io import BytesIO as _BytesIO
from json import dumps as _dumps, loads as _loads
from os.path import basename as _basename
from pathlib import Path as _Path
from sys import argv as _argv, exit as _exit, stderr as _stderr
from socket import inet_aton as _inet_aton
from time import time as _time
from uuid import uuid4 as _uuid4
from aiohttp import request as _request
from aiohttp.web import Application as _Application, \
Response as _Response, RouteTableDef as _RouteTableDef, \
GracefulExit as _GracefulExit, run_app as _run_app
from aiohttp_session import get_session as _get_session, setup as _setup
from aiohttp_session import SimpleCookieStorage as _SimpleCookieStorage
from PIL.Image import open as _open
from pyzbar.pyzbar import decode as _decode, ZBarSymbol as _ZBarSymbol
from xdcheckin.core.chaoxing import Chaoxing as _Chaoxing
from xdcheckin.core.locations import locations as _locations
from xdcheckin.core.xidian import IDSSession as _IDSSession, \
Newesxidian as _Newesxidian
from xdcheckin.util.types import TimestampDict as _TimestampDict
from xdcheckin.util.version import compare_versions as _compare_versions, \
version as _version

server_routes = _RouteTableDef()
_locations_str = _dumps(_locations).encode("ascii").decode("unicode-escape")
_static_g_locations_js_str = f"var g_locations = {_locations_str};"
@server_routes.get("/static/g_locations.js")
async def _static_g_locations_js(req):
	return _Response(
		text = _static_g_locations_js_str,
		content_type = "text/javascript", charset = "utf-8"
	)

with _Path(__file__).parent.resolve() as path:
	server_routes.static("/static", path.joinpath("static"))
	_index_html_str = \
	path.joinpath("templates", "index.html").read_text(encoding = "utf-8")
@server_routes.get("/")
async def _index_html(req):
	return \
	_Response(text = _index_html_str, content_type = "text/html")

@server_routes.post("/xdcheckin/get_version")
async def _xdcheckin_get_version(req):
	return _Response(text = _version)

_xdcheckin_get_update_time = 0
_xdcheckin_get_update_data = ""
@server_routes.post("/xdcheckin/get_update")
async def _xdcheckin_get_update(req):
	global _xdcheckin_get_update_time, _xdcheckin_get_update_data
	update, time = False, _time()
	if 1 or time < _xdcheckin_get_update_time + 3600:
		_xdcheckin_get_update_time = time
		try:
			async with _request(
				"GET",
				"https://api.github.com/repos/Pairman/Xdcheckin/releases/latest"
			) as res:
				assert res.status == 200
				data = await res.json()
			update = _compare_versions(
				_version, data["tag_name"]
			) == 1
		except Exception:
			update = False
		_xdcheckin_get_update_data = _dumps({
			"tag_name": data["tag_name"],
			"name": data["name"],
			"author": data["author"]["login"],
			"body": data["body"].replace("\r\n", "<br>"),
			"published_at": data["published_at"],
			"html_url": data["html_url"],
			"assets": [{
				"name": asset["name"],
				"size": asset["size"],
				"browser_download_url":
				asset["browser_download_url"]
			} for asset in data["assets"]],
			"updatable": True
		}) if update else _dumps({"updatable": False})
	return _Response(
		text = _xdcheckin_get_update_data,
		content_type = "application/json",
		status = 200 if _xdcheckin_get_update_data else 500
	)

@server_routes.post("/ids/login_prepare")
async def _ids_login_prepare(req):
	try:
		ids = _IDSSession(
			service = "https://learning.xidian.edu.cn/cassso/xidian"
		)
		await ids.__aenter__()
		ses = await _get_session(req)
		ses.setdefault("uuid", str(_uuid4()))
		req.app["config"]["sessions"].setdefault(
			ses["uuid"], {}
		)["ids"] = ids
		data = await ids.login_username_prepare()
	except Exception as e:
		_create_task(ids.__aexit__(None, None, None))
		data = {"err": str(e)}
	finally:
		return _Response(
			text = _dumps(data), content_type = "application/json"
		)

@server_routes.post("/ids/login_finish")
async def _ids_login_finish(req):
	try:
		data = await req.json()
		username, password, vcode = \
		data["username"], data["password"], data["vcode"]
		assert username and password and vcode, \
		"Missing username, password or verification code."
		ses = await _get_session(req)
		ids = req.app["config"]["sessions"][ses["uuid"]].pop("ids")
		ret = await ids.login_username_finish(account = {
			"username": username, "password": password,
			"vcode": vcode
		})
		_create_task(ids.__aexit__(None, None, None))
		assert ret["logged_in"], "IDS login failed."
		cookies = ret["cookies"].filter_cookies("https://chaoxing.com")
		return await _chaoxing_login(req = req, data = {
			"username": "", "password": "", "cookies":
			_dumps({k: v.value for k, v in cookies.items()})
		})
	except Exception as e:
		return _Response(
			text = _dumps({"err": str(e)}),
			content_type = "application/json"
		)

@server_routes.post("/chaoxing/login")
async def _chaoxing_login(req, data = None):
	try:
		if not data:
			data = await req.json()
		username, password, cookies = \
		data["username"], data["password"], data["cookies"]
		assert (username and password) or cookies, \
		"Missing username, password or cookies."
		config = {
			"chaoxing_course_get_activities_courses_limit": 36,
			"chaoxing_checkin_location_address_override_maxlen": 13
		}
		cx = _Chaoxing(
			username = username, password = password,
			cookies = _loads(cookies) if cookies else None,
			config = config
		)
		await cx.__aenter__()
		assert cx.logged_in, "Chaoxing login failed."
		ses = await _get_session(req)
		ses.setdefault("uuid", str(_uuid4()))
		req.app["config"]["sessions"].setdefault(
			ses["uuid"], {}
		)["cx"] = cx
		if cx.fid == "16820":
			nx = _Newesxidian(chaoxing = cx)
			req.app["config"]["sessions"][ses["uuid"]]["nx"] = nx
			_create_task(nx.__aenter__())
		data = {
			"fid": cx.fid, "courses": cx.courses, "cookies":
			_dumps({k: v.value for k, v in cx.cookies.items()})
		}
	except Exception as e:
		data = {"err": str(e)}
	finally:
		return _Response(
			text = _dumps(data), content_type = "application/json"
		)

@server_routes.post("/newesxidian/extract_url")
async def _newesxidian_extract_url(req):
	try:
		data = await req.json()
		ses = await _get_session(req)
		nx = req.app["config"]["sessions"][ses["uuid"]]["nx"]
		assert nx.logged_in
		livestream = await nx.livestream_get_live_url(
			livestream = {"live_id": str(data)}
		)
		return _Response(text = livestream["url"])
	except Exception as e:
		return _Response(text = "")

@server_routes.post("/chaoxing/get_curriculum")
async def _chaoxing_get_curriculum(req):
	try:
		with_live = await req.json()
		ses = await _get_session(req)
		xx = req.app["config"]["sessions"][ses["uuid"]][
			"nx" if with_live else "cx"
		]
		assert xx.logged_in
		data = await xx.curriculum_get_curriculum()
		status = 200
	except Exception:
		data = {}
		status = 500
	finally:
		return _Response(
			text = _dumps(data), status = status,
			content_type = "application/json"
		)

@server_routes.post("/chaoxing/get_activities")
async def _chaoxing_get_activities(req):
	try:
		ses = await _get_session(req)
		cx = req.app["config"]["sessions"][ses["uuid"]]["cx"]
		assert cx.logged_in
		data = await cx.course_get_activities()
		status = 200
	except Exception:
		data = {}
		status = 500
	finally:
		return _Response(
			text = _dumps(data), status = status,
			content_type = "application/json"
		)

@server_routes.post("/chaoxing/captcha_get_captcha")
async def _chaoxing_captcha_get_captcha(req):
	try:
		data = await req.json()
		assert data["captcha"]
		ses = await _get_session(req)
		cx = req.app["config"]["sessions"][ses["uuid"]]["cx"]
		assert cx.logged_in
		data = await cx.captcha_get_captcha(captcha = data["captcha"])
		status = 200
	except Exception:
		data = {}
		status = 500
	finally:
		return _Response(
			text = _dumps(data), status = status,
			content_type = "application/json"
		)

@server_routes.post("/chaoxing/captcha_submit_captcha")
async def _chaoxing_captcha_submit_captcha(req):
	try:
		data = await req.json()
		assert data["captcha"]
		ses = await _get_session(req)
		cx = req.app["config"]["sessions"][ses["uuid"]]["cx"]
		assert cx.logged_in
		data = \
		await cx.captcha_submit_captcha(captcha = data["captcha"])
		assert data[0]
		data = data[1]
		status = 200
	except Exception:
		data = {}
		status = 500
	finally:
		return _Response(
			text = _dumps(data), status = status,
			content_type = "application/json"
		)

@server_routes.post("/chaoxing/checkin_do_sign")
async def _chaoxing_checkin_do_sign(req):
	try:
		data = await req.json()
		assert data["params"], "No parameters given."
		ses = await _get_session(req)
		cx = req.app["config"]["sessions"][ses["uuid"]]["cx"]
		assert cx.logged_in, "Not logged in."
		result = await cx.checkin_do_sign(old_params = data["params"])
		data = result[1]
	except Exception as e:
		data = {"msg": f"Checkin error. ({str(e)})", "params": {}}
	finally:
		return _Response(
			text = _dumps(data), content_type = "application/json"
		)
					

@server_routes.post("/chaoxing/checkin_checkin_location")
async def _chaoxing_checkin_checkin_location(req):
	try:
		data = await req.json()
		assert data["activity"]["active_id"], "No activity ID given."
		ses = await _get_session(req)
		cx = req.app["config"]["sessions"][ses["uuid"]]["cx"]
		assert cx.logged_in, "Not logged in."
		data["activity"]["active_id"] = \
		str(data["activity"]["active_id"])
		result = await cx.checkin_checkin_location(
			activity = data["activity"], location = data["location"]
		)
		data = result[1]
	except Exception as e:
		data = {
			"msg": f"Checkin error. ({str(e)})", "params": {},
			"captcha": {}
		}
	finally:
		return _Response(
			text = _dumps(data), content_type = "application/json"
		)

@server_routes.post("/chaoxing/checkin_checkin_qrcode_img")
async def _chaoxing_checkin_checkin_qrcode_img(req):
	try:
		ses = await _get_session(req)
		cx = req.app["config"]["sessions"][ses["uuid"]]["cx"]
		assert cx.logged_in, "Not logged in."
		location = img_data = img = None
		form = await req.multipart()
		field = await form.next()
		assert field.name == "location"
		location = _loads(await field.text())
		field = await form.next()
		assert location, "No location given."
		assert field.name == "img_src"
		img_data = _BytesIO()
		while True:
			chk = await field.read_chunk()
			if not chk:
				break
			img_data.write(chk)
		assert img_data.getbuffer().nbytes, "No image given."
		img_data.seek(0)
		img = _open(img_data)
		assert img.height > 64 and img.width > 64, "Empty image."
		urls = _decode(img, (_ZBarSymbol.QRCODE, ))
		assert urls, "No Qrcode detected."
		urls = [
			s.data.decode("utf-8") for s in urls
			if b"mobilelearn.chaoxing.com/widget/sign/e" in s.data
		]
		assert urls, "No checkin URL found."
		result = await cx.checkin_checkin_qrcode_url(
			url = urls[0], location = location
		)
		data = result[1]
	except Exception as e:
		data = {
			"msg": f"Checkin error. ({str(e)})", "params": {},
			"captcha": {}
		}
	finally:
		if img_data:
			img_data.close()
		if img:
			img.close()
		return _Response(
			text = _dumps(data), content_type = "application/json"
		)

async def _vacuum_server_sessions_handler(ses):
	for key in {"ids", "nx", "cx"}:
		if key in ses:
			await ses[key].__aexit__(None, None, None)

async def _vacuum_server_sessions(app):
	sessions = app["config"]["sessions"]
	t = app["config"]["sessions_vacuum_days"] * 86400 \
	- 18000 - _time() % 86400
	if t <= 0:
		return
	while True:
		await _sleep(t)
		_create_task(sessions.vacuum(
			seconds = t,
			handler = _vacuum_server_sessions_handler
		))

def create_server(config: dict = {}):
	"""Create a Xdcheckin server.
	:param config: Configurations.
	:return: Xdcheckin server.
	"""
	app = _Application()
	app.add_routes(server_routes)
	app["config"] = {"sessions": {}, "sessions_vacuum_days": 1, **config}
	_setup(app, _SimpleCookieStorage(
		cookie_name = "xdcheckin", max_age = 604800
	))
	return app

def start_server(host: str = "0.0.0.0", port: int = 5001, config: dict = {}):
	"""Run a Xdcheckin server.
	:param host: IP address.
	:param port: Port.
	:param config: Configurations.
	"""
	app = create_server(config = {"sessions": _TimestampDict(), **config})
	async def _startup(app):
		app["config"]["_vacuum_task"] = \
		_create_task(_vacuum_server_sessions(app = app))
		print(f"Starting Xdcheckin server on {host}:{port}.")
	async def _cleanup(app):
		print("Shutting down Xdcheckin server.")
		await app["config"]["sessions"].vacuum(
			handler = _vacuum_server_sessions_handler
		)
		_GracefulExit()
	app.on_startup.append(_startup)
	app.on_cleanup.append(_cleanup)
	_run_app(
		app, host = host, port = port,
		print = lambda _: print("Server started. Press Ctrl+C to quit.")
	)

def _main():
	bn = _basename(_argv[0])
	help = \
	f"xdcheckin-server - Xdcheckin Server Commandline Tool " \
	f"{_version}\n\n" \
	f"Usage: \n" \
	f"  {bn} [<host> <port>]\tStart server on the given host and port.\n" \
	f"  {' ' * len(bn)}\t\t\t'0.0.0.0:5001' by default.\n" \
	f"  {bn} -h\t\t\tShow help. Also '--help'."
	if len(_argv) == 2 and _argv[1] in ("-h", "--help"):
		print(help)
		_exit()
	elif not len(_argv) in (1, 3):
		print(help, file = _stderr)
		_exit(2)
	host, port = "0.0.0.0", 5001
	if len(_argv) == 3:
		try:
			host = _argv[1]
			_inet_aton(host)
		except Exception:
			print(f"Invalid IP address {host}", file = _stderr)
			_exit(2)
		try:
			port = int(_argv[2])
			assert 0 < port < 65536
		except Exception:
			print(f"Invalid port number {port}", file = _stderr)
			_exit(2)
	start_server(host = host, port = port)
