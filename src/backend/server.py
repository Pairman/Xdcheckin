from flask import Flask, render_template, make_response, session
from flask_session import Session
from json import loads, dumps
from os import listdir, remove
import requests
from tempfile import gettempdir
from backend.xdcheckin_py.chaoxing.chaoxing import Chaoxing
from backend.xdcheckin_py.chaoxing.locations import locations

requests.packages.urllib3.disable_warnings()

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

@server.route("/xdcheckin/get/locations.js")
def get_xdcheckin_locations_js():
	res = make_response("var locations = " + dumps(locations).encode("ascii").decode("unicode-escape") + ";")
	res.status_code = 200
	return res

@server.route("/xdcheckin/get/classrooms.js")
def get_xdcheckin_classrooms_js(cmd = ""):
	cmd = cmd.replace("::", "/")
	try:
		res = requests.get("https://xdcheckin.git.pnxlr.eu.org/src/backend/static/classrooms.js")
		assert res.status_code == 200
		res = make_response(res.text)
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@server.route("/xdcheckin/get/version")
def get_xdcheckin_version():
	res = make_response(server.config["version"])
	res.status_code = 200
	return res

@server.route("/xdcheckin/get/releases/latest")
def get_xdcheckin_latest_release():
	try:
		res = requests.get("https://api.github.com/repos/Pairman/Xdcheckin/releases")
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

@server.route("/")
@server.route("/index.html")
def index_html():
	return render_template("index.html")

@server.route("/player.html")
def player_html():
	return render_template("player.html")

@server.route("/chaoxing/login/<cmd>")
def chaoxing_login(cmd: str = "{\"username\": \"\", \"password\": \"\"}"):
	try:
		params = loads(cmd)
		username, password = params["username"], params["password"]
		assert username and password
		chaoxing = Chaoxing(username, password)
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
		assert chaoxing.logined
		fid = chaoxing.fid
		assert fid
		res = make_response(fid)
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
		courses = chaoxing.courses
		assert courses
		res = make_response(dumps(courses))
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/get_curriculum")
def chaoxing_get_curriculum():
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined
		curriculum = chaoxing.get_curriculum()
		assert curriculum
		res = make_response(dumps(curriculum))
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/get_activities")
def chaoxing_get_activities():
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined
		activities = chaoxing.get_activities()
		assert activities
		res = make_response(dumps(activities))
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/checkin_checkin_location/<cmd>")
def chaoxing_checkin_checkin_location(cmd: str = "{\"active_id\": \"\", \"location\": {\"latitude\": -1, \"longitude\": -1, \"address\": \"\"}}"):
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined
		params = loads(cmd)
		active_id, location = params["active_id"], params.get("location") or {"latitude": -1, "longitude": -1, "address": ""}
		assert active_id and location
		assert chaoxing.checkin_checkin_location({"active_id": active_id}, location)
		res = make_response("success")
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/checkin_checkin_qrcode/<cmd>")
def chaoxing_checkin_checkin_qrcode(cmd: str = "{\"active_id\": \"\", \"enc\": \"\", \"location\": {\"latitude\": -1, \"longitude\": -1, \"address\": \"\"}}"):
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined
		params = loads(cmd)
		active_id, enc, location = params["active_id"], params["enc"], params.get("location") or {"latitude": -1, "longitude": -1, "address": ""}
		assert active_id and enc and location
		assert chaoxing.checkin_checkin_qrcode({"active_id": active_id, "enc": enc}, location)
		res = make_response("success")
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@server.route("/chaoxing/extract_url/<cmd>")
def chaoxing_extract_url(cmd: str = ""):
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined
		res = chaoxing.get("https://newesxidian.chaoxing.com/live/getViewUrlHls?liveId=" + cmd)
		assert res.status_code == 200
		res = make_response(res.text)
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

if __name__ == "__main__":
	server.run(host = "0.0.0.0", port=5001)
