from base64 import b64decode
from flask import Flask, render_template, make_response, request, session
from flask_session import Session
from io import BytesIO
from json import loads, dumps
from os import listdir, remove
from PIL.Image import open as Image_open
from pyzbar.pyzbar import decode
from requests import get
from requests.utils import add_dict_to_cookiejar
from tempfile import gettempdir
from backend.xdcheckin_py.chaoxing.chaoxing import Chaoxing
from backend.xdcheckin_py.chaoxing.locations import locations

server = Flask(__name__)
server.config["SESSION_PERMANENT"] = False
server.config["SESSION_TYPE"] = "filesystem"
server.config["SESSION_FILE_DIR"] = gettempdir() + "/xdcheckin"
server.config["version"] = "0.0.0"

try:
	for i in listdir(server.config["SESSION_FILE_DIR"]):
		try:
			remove(server.config["SESSION_FILE_DIR"] + "/" + i)
		except Exception:
			continue
except Exception:
	pass

Session(server)

@server.route("/")
@server.route("/index.html")
def index_html():
	return render_template("index.html")

@server.route("/player.html")
def player_html():
	return render_template("player.html")

@server.route("/xdcheckin/get/locations.js")
def get_xdcheckin_locations_js():
	res = make_response("var locations = " + dumps(locations).encode("ascii").decode("unicode-escape") + ";")
	res.status_code = 200
	return res

@server.route("/xdcheckin/get/version")
def get_xdcheckin_version():
	res = make_response(server.config["version"])
	res.status_code = 200
	return res

@server.route("/xdcheckin/get/releases/latest")
def get_xdcheckin_latest_release():
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
		chaoxing = session["chaoxing"]
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
		chaoxing = Chaoxing(username = username, password = password, cookies = add_dict_to_cookiejar(None, loads(cookies)) if cookies else None)
		if not chaoxing.logined:
			chaoxing = Chaoxing(username = username, password = password)
		assert chaoxing.logined
		session["chaoxing"] = chaoxing
		res = make_response("success")
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/get_fid")
def chaoxing_get_fid():
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined and chaoxing.fid
		res = make_response(chaoxing.fid)
		res.status_code = 200
	except Exception:
		res = make_response("0")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/get_cookies")
def chaoxing_get_cookies():
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined and chaoxing.cookies
		res = make_response(dumps(dict(chaoxing.cookies)))
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/get_courses")
def chaoxing_get_courses():
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined
		res = make_response(dumps(chaoxing.courses))
		res.status_code = 200
	except Exception:
		res = make_response("{}")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/get_curriculum")
def chaoxing_get_curriculum():
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined
		res = make_response(dumps(chaoxing.get_curriculum()))
		res.status_code = 200
	except Exception:
		res = make_response("{}")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/get_activities")
def chaoxing_get_activities():
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined
		activities = chaoxing.get_activities()
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
		chaoxing = session["chaoxing"]
		assert chaoxing.logined
		data = request.get_json(force = True)
		assert data["activity"]["active_id"]
		assert chaoxing.checkin_checkin_location(activity = data["activity"], location = data.get("location") or {"latitude": -1, "longitude": -1, "address": ""})
		res = make_response("success")
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/checkin_checkin_qrcode_img", methods = ["POST"])
def chaoxing_checkin_checkin_qrcode_img():
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined, "Not logged in."
		data = request.get_json(force = True)
		assert data["img_src"], "No image given."
		img_src = data["img_src"].split(",")[1]
		assert img_src, "No image given."
		qr_urls = [s.data.decode("utf-8") for s in decode(Image_open(BytesIO(b64decode(img_src)))) if b"mobilelearn.chaoxing.com/widget/sign/e" in s.data]
		assert qr_urls, "No checkin URL found."
		res = make_response(("Checked in successfully:\n" if chaoxing.checkin_checkin_qrcode_url(qr_url = qr_urls[0], location = data.get("location") or {"latitude": -1, "longitude": -1, "address": ""}) else "Checkin failed:\n") + qr_urls[0])
	except Exception as e:
		res = make_response("Checkin Error:\n" + str(e))
	finally:
		res.status_code = 200
		return res
