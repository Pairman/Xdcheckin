from flask import Flask, render_template, make_response, session
from flask_session import Session
from json import loads, dumps
from os import listdir, remove
import requests
from tempfile import gettempdir
from xdcheckin.Xdcheckin.xdcheckin_py.chaoxing.chaoxing import Chaoxing

requests.packages.urllib3.disable_warnings()

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = gettempdir() + "/xdcheckin"

for i in listdir(app.config["SESSION_FILE_DIR"]):
	try:
		remove(app.config["SESSION_FILE_DIR"] + "/" + i)
	except Exception:
		continue

Session(app)

@app.route("/get/xdclassroom/<cmd>")
def get_xdclassroom(cmd = ""):
	cmd = cmd.replace("::", "/")
	try:
		res = requests.get("https://xdclassroom.git.pnxlr.eu.org/" + cmd)
		assert res.status_code == 200
		res = make_response(res.text)
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@app.route("/")
@app.route("/index.html")
def index_html():
	return get_xdclassroom("index.html")

@app.route("/player.html")
def player_html():
	return render_template("player.html")

@app.route("/chaoxing/login/<cmd>")
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

@app.route("/chaoxing/get_courses")
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

@app.route("/chaoxing/get_curriculum")
def chaoxing_get_curriculum():
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined
		curriculum = chaoxing.curriculum
		assert curriculum
		res = make_response(dumps(curriculum))
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

@app.route("/chaoxing/get_activities")
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

@app.route("/chaoxing/checkin_checkin_location/<cmd>")
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

@app.route("/chaoxing/checkin_checkin_qrcode/<cmd>")
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

if __name__ == "__main__":
	app.run(host = "0.0.0.0", port=5001)
