from flask import Flask, render_template, make_response, request, session
from flask_session import Session
from importlib.metadata import version
from io import BytesIO
from json import loads, dumps
from PIL.Image import open
from pyzbar.pyzbar import decode
from requests import get
from urllib3 import disable_warnings
from waitress import serve
from xdcheckin.core.chaoxing import Chaoxing
from xdcheckin.core.xidian import Newesxidian
from xdcheckin.core.locations import locations

def create_server():
	server = Flask(__name__)
	server.config["SESSION_PERMANENT"] = False

	Session(server)

	@server.route("/")
	@server.route("/player.html")
	def player_html():
		return render_template("player.html")

	@server.route("/xdcheckin/static/locations.js")
	def xdcheckin_static_locations_js():
		res = make_response(f"var locations = {dumps(locations).encode('ascii').decode('unicode-escape')};")
		res.status_code = 200
		return res

	@server.route("/xdcheckin/get/version", methods = ["POST"])
	def xdcheckin_get_version():
		res = make_response(version("Xdcheckin"))
		res.status_code = 200
		return res

	@server.route("/xdcheckin/get/releases/latest", methods = ["POST"])
	def xdcheckin_get_latest_release():
		try:
			res = get("https://api.github.com/repos/Pairman/Xdcheckin/releases/latest")
			assert res.status_code == 200
			data = res.json()
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

	@server.route("/chaoxing/login", methods = ["POST"])
	def chaoxing_login():
		try:
			data = request.get_json(force = True)
			username, password, cookies = data["username"], data["password"], data["cookies"]
			assert (username and password) or cookies
			session["chaoxing"] = Chaoxing(username = username, password = password, cookies = loads(cookies) if cookies else None)
			assert session["chaoxing"].logined
			session["newesxidian"] = Newesxidian(chaoxing = session["chaoxing"])
			res = make_response(dumps({
				"fid": session["chaoxing"].cookies.get("fid") or "0",
				"courses": session["chaoxing"].courses,
				"cookies": dumps(dict(session["chaoxing"].cookies))
			}))
		except Exception as e:
			res = make_response(dumps({"err": str(e)}))
		finally:
			res.status_code = 200
			return res

	@server.route("/chaoxing/extract_url", methods = ["POST"])
	def chaoxing_extract_url():
		try:
			assert session["chaoxing"].logined
			data = request.get_json(force = True)
			assert data
			livestream = session["newesxidian"].livestream_get_live_url(livestream = {"live_id": str(data)})
			res = make_response(livestream["url"])
			res.status_code = 200
		except Exception:
			res = make_response("")
			res.status_code = 500
		finally:
			return res

	@server.route("/chaoxing/get_curriculum", methods = ["POST"])
	def chaoxing_get_curriculum():
		try:
			assert session["chaoxing"].logined
			curriculum = session["newesxidian"].curriculum_get_curriculum() if session["newesxidian"].logined else session["chaoxing"].curriculum_get_curriculum()
			res = make_response(dumps(curriculum))
			res.status_code = 200
		except Exception as e:
			print(str(e))
			res = make_response("{}")
			res.status_code = 500
		finally:
			return res

	@server.route("/chaoxing/get_activities", methods = ["POST"])
	def chaoxing_get_activities():
		try:
			assert session["chaoxing"].logined
			activities = session["chaoxing"].course_get_activities()
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
			assert session["chaoxing"].logined, "Not logged in."
			data = request.get_json(force = True)
			assert data["activity"]["active_id"], "No activity ID given."
			data["activity"]["active_id"] = str(data["activity"]["active_id"])
			result = session["chaoxing"].checkin_checkin_location(activity = data["activity"], location = data["location"])
			res = make_response(f"{result[1][: -1]}, {data['activity']['active_id']})")
		except Exception as e:
			res = make_response(f"Checkin error. ({str(e)})")
		finally:
			res.status_code = 200
			return res

	@server.route("/chaoxing/checkin_checkin_qrcode_img", methods = ["POST"])
	def chaoxing_checkin_checkin_qrcode_img():
		try:
			assert session["chaoxing"].logined, "Not logged in."
			img_src = request.files["img_src"]
			assert img_src, "No image given."
			with open(BytesIO(img_src.read())) as img:
				assert img.size[0] > 0 and img.size[1] > 0, "Empty image."
				urls = decode(img)
			assert urls, "No Qrcode detected."
			urls = tuple(s.data.decode("utf-8") for s in urls if b"mobilelearn.chaoxing.com/widget/sign/e" in s.data)
			assert urls, "No checkin URL found."
			result = session["chaoxing"].checkin_checkin_qrcode_url(url = urls[0], location = loads(request.form["location"]))
			res = make_response(f"{result[1][: -1]}, {urls[0]})")
		except Exception as e:
			res = make_response(f"Checkin error. ({str(e)})")
		finally:
			res.status_code = 200
			return res

	return server

def start_server(host: str = "127.0.0.1", port: int = 5001):
	disable_warnings()
	serve(app = create_server(), host = host, port = port)

def main():
	from sys import argv

	if not len(argv) in (1, 3):
		print(f"xdcheckin-server - Xdcheckin Server Commandline Tool {version('Xdcheckin')}")
		print(f"Usage: {argv[0]} <ip> <port>")
		print(f"  or:  {argv[0]}")
		return 1
	ip, port = "0.0.0.0", 5001
	if len(argv) == 3:
		from socket import inet_aton
		try:
			ip = argv[1]
			inet_aton(ip)
		except Exception:
			print(f"Invalid IP address {ip}")
			return 1
		try:
			port = int(argv[2])
			assert 0 < port < 65536
		except Exception:
			print(f"Invalid port number {port}")
			return 1

	print(f"Starting server at {ip}:{port}")
	start_server(host = ip, port = port)
