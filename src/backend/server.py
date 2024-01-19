from atexit import register
from base64 import b64decode
from flask import Flask, render_template, make_response, request, session
from flask_session import Session
from io import BytesIO
from json import loads, dumps
from os import listdir, remove, makedirs
from os.path import exists
from PIL.Image import open as Image_open
from pyzbar.pyzbar import decode
from requests import get
from tempfile import gettempdir
from backend.xdcheckin_py.chaoxing.chaoxing import Chaoxing
from backend.xdcheckin_py.chaoxing.locations import locations

server = Flask(__name__)
server.config.update({
	"SESSION_PERMANENT": False,
	"SESSION_TYPE": "filesystem",
	"SESSION_FILE_DIR": gettempdir() + "/xdcheckin"
})

if not exists(server.config["SESSION_FILE_DIR"]):
	makedirs(server.config["SESSION_FILE_DIR"])
else:
	for i in listdir(server.config["SESSION_FILE_DIR"]):
		try:	
			remove(server.config["SESSION_FILE_DIR"] + "/" + i)
		except Exception:	
			continue

Session(server)

@server.route("/blank.html")
def blank_html():
	return render_template("blank.html")

@server.route("/")
@server.route("/player.html")
def player_html():
	return render_template("player.html")

@server.route("/xdcheckin/static/locations.js")
def xdcheckin_static_locations_js():
	res = make_response("var locations = " + dumps(locations).encode("ascii").decode("unicode-escape") + ";")
	res.status_code = 200
	return res

@server.route("/xdcheckin/get/version", methods = ["POST"])
def xdcheckin_get_version():
	res = make_response(server.config.get("XDCHECKIN_VERSION") or "0.0.0")
	res.status_code = 200
	return res

@server.route("/xdcheckin/get/releases/latest", methods = ["POST"])
def xdcheckin_get_latest_release():
	try:
		res = get("https://api.github.com/repos/Pairman/Xdcheckin/releases")
		assert res.status_code == 200
		data = res.json()[0]
		res = make_response(dumps({
			"tag_name": data["tag_name"],
			"name": data["name"],
			"author": data["author"]["login"],
			"body": data["body"],
			"published_at": data["published_at"],
			"html_url": data["html_url"],
			"assets": [{
					"name": asset["name"],
					"size": asset["size"],
					"browser_download_url": asset["browser_download_url"]
				} for asset in data["assets"]]
		}))
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/extract_url", methods = ["POST"])
def chaoxing_extract_url():
	try:
		assert chaoxing.logined
		data = request.get_json(force = True)
		assert data
		res = chaoxing.get("https://newesxidian.chaoxing.com/live/getViewUrlHls", params = {"liveId": data})
		assert res.status_code == 200
		res = make_response(res.text)
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/login", methods = ["POST"])
def chaoxing_login():
	try:
		data = request.get_json(force = True)
		username, password, cookies = data["username"], data["password"], data["cookies"]
		assert (username and password) or cookies
		global chaoxing
		chaoxing = Chaoxing(username = username, password = password, cookies = loads(cookies) if cookies else None)
		assert chaoxing.logined
		res = make_response(dumps({"fid": chaoxing.cookies.get("fid") or "0", "courses": chaoxing.courses, "curriculum": chaoxing.curriculum_get_curriculum(), "cookies": dumps(dict(chaoxing.cookies))}))
	except Exception as e:
		res = make_response(dumps({"err": (type(e), e, e.__traceback__)}))
	finally:
		res.status_code = 200
		return res

@server.route("/chaoxing/get_activities", methods = ["POST"])
def chaoxing_get_activities():
	try:
		assert chaoxing.logined
		activities = chaoxing.course_get_activities()
		res = make_response(dumps(activities))
		res.status_code = 200
	except Exception:
		res = make_response("{}")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/checkin_checkin_location", methods = ["POST"])
def chaoxing_checkin_checkin_location():
	try:
		assert chaoxing.logined, "Not logged in."
		data = request.get_json(force = True)
		assert data["activity"]["active_id"], "No activity ID given."
		result = chaoxing.checkin_checkin_location(activity = data["activity"], location = data.get("location") or {"latitude": -1, "longitude": -1, "address": ""})
		res = make_response(result[1])
	except Exception as e:
		res = make_response("Checkin error. (" + str(e) + ")")
	finally:
		res.status_code = 200
		return res

@server.route("/chaoxing/checkin_checkin_qrcode_img", methods = ["POST"])
def chaoxing_checkin_checkin_qrcode_img():
	try:
		assert chaoxing.logined, "Not logged in."
		data = request.get_json(force = True)
		assert data["img_src"], "No image given."
		img_src = data["img_src"].split(",")[1]
		assert img_src, "No image given."
		urls = decode(Image_open(BytesIO(b64decode(img_src))))
		assert urls, "No Qrcode detected."
		urls = tuple(s.data.decode("utf-8") for s in urls if b"mobilelearn.chaoxing.com/widget/sign/e" in s.data)
		assert urls, "No checkin URL found."
		result = chaoxing.checkin_checkin_qrcode_url(url = urls[0], location = data.get("location") or {"latitude": -1, "longitude": -1, "address": ""})
		res = make_response(result[1][:-1] + ", " + urls[0] + ")")
	except Exception as e:
		res = make_response("Checkin error. (" + str(e) + ")")
	finally:
		res.status_code = 200
		return res
