from flask import Flask, render_template, make_response, session
from flask_session import Session
from json import loads, dumps
from chaoxing.chaoxing import *
import requests

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

requests.packages.urllib3.disable_warnings()

@app.route("/")
@app.route("/index.html")
def index_html():
	return render_template("index.html")

@app.route("/player.html")
def player_html():
	return render_template("player.html")

@app.route("/chaoxing/login/<cmd>")
def chaoxing_login(cmd: str = "\{\"username\": \"\", \"password\": \"\""):
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

@app.route("/chaoxing/checkin_checkin_qrcode_url/<cmd>")
def chaoxing_checkin_checkin_qrcode_url(cmd: str = "{\"qr_url\": \"\", \"location\": {\"latitude\": -1, \"longitude\": -1, \"address\": \"\"}}"):
	try:
		chaoxing = session["chaoxing"]
		assert chaoxing.logined
		params = loads(cmd)
		qr_url, location = params["qr_url"], params.get("location") or {"latitude": -1, "longitude": -1, "address": ""}
		assert qr_url and location
		assert chaoxing.checkin_checkin_qrcode_url(qr_url, location)
		res = make_response("success")
		res.status_code = 200
	except Exception:
		res = make_response("")
		res.status_code = 500
	finally:
		return res

if __name__ == "__main__":
	app.run(host = "0.0.0.0", port=5001)
