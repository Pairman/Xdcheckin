# -*- coding: utf-8 -*-

from base64 import b64encode
from Crypto.Cipher.AES import new as AES_new, block_size as AES_block_size, MODE_CBC as AES_MODE_CBC
from Crypto.Util.Padding import pad as pad_pkcs7
from json import dumps
from re import findall, search, DOTALL
from requests import get, post
from threading import Thread
from time import sleep
from urllib.parse import parse_qs, unquote, urlparse

class Chaoxing:
	name = cookies = courses = logined = None
	headers = {
		"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
	}

	def __init__(self, username: str = "", password: str = "", cookies = None):
		"""Create a Chaoxing instance and login.
		:param username: Chaoxing username. Unused if cookies are given.
		:param password: Chaoxing password. Unused if cookies are given.
		:param cookies: Cookies from previous login. Overrides username and password if given.
		:return: None.
		"""
		if self.logined:
			return
		self.name, self.cookies, self.logined = (self.login_cookies if cookies else self.login_username_fanya)(account = {"username": username, "password": password, "cookies": cookies}).values()
		self.courses = self.course_get_courses() if self.logined else {}

	def get(self, url: str = "", params: dict = {}, cookies = None, headers: dict = None, verify: bool = False):
		"""Wrapper for requests.get().
		:param url: URL.
		:param params: Parameters.
		:cookies: Cookies. Overrides existing cookies.
		:headers: Headers. Overrides existing headers.
		:verify: SSL certificate verification toggle. False by default.
		:return: Response object.
		"""
		cookies = cookies if cookies else self.cookies
		headers = headers if headers else self.headers
		return get(url, params = params, cookies = cookies, headers = headers, verify = False)

	def post(self, url: str = "", data: dict = {}, params: dict = {}, cookies = None, headers: dict = None, verify: bool = False):
		"""Wrapper for requests.post().
		:param url: URL.
		:param data: Data.
		:param params: Parameters.
		:cookies: Cookies. Overrides existing cookies.
		:headers: Headers. Overrides existing headers.
		:verify: SSL certificate verification toggle. False by default.
		:return: Response object.
		"""
		cookies = cookies if cookies else self.cookies
		headers = headers if headers else self.headers
		return post(url, data = data, params = params, cookies = cookies, headers = headers, verify = False)

	def login_username_v2(self, account: dict = {"username": "", "password": ""}):
		"""Log into Chaoxing account with username and password via V2 API.
		:param account: Username and password in dictionary.
		:return: Name, cookies and login state.
		"""
		url = "https://passport2-api.chaoxing.com/api/v2/loginbypwd"
		params = {
			"name": account["username"],
			"pwd": account["password"]
		}
		try:
			res = self.get(url = url, params = params)
			data = res.json()
			assert data["result"]
			return {
				"name": data["realname"],
				"cookies": res.cookies,
				"logined": True
			}
		except Exception:
			return {
				"name": "",
				"cookies": None,
				"logined": False
			}

	def login_username_v3(self, account: dict = {"username": "", "password": ""}):
		"""Log into Chaoxing account with username and password via V3 API.
		:param account: Same as login_username_v2().
		:return: Name (placeholder), cookies and login state.
		"""
		url = "http://v3.chaoxing.com/vLogin"
		data = {
			"userNumber": account["username"],
			"passWord": account["password"]
		}
		try:
			res = self.post(url = url, data = data)
			assert res.json()["status"]
			return {
				"name": "",
				"cookies": res.cookies,
				"logined": True
			}
		except Exception:
			return {
				"name": "",
				"cookies": None,
				"logined": False
			}

	def login_username_v11(self, account: dict = {"username": "", "password": ""}):
		"""Log into Chaoxing account with username and password via V11 API.
		:param account: Same as login_username_v2().
		:return: Same as login_username_v3().
		"""
		url = "https://passport2-api.chaoxing.com/v11/loginregister"
		params = {
			"uname": account["username"],
			"code": account["password"]
		}
		try:
			res = self.get(url = url, params = params)
			assert res.json()["status"]
			return {
				"name": "",
				"cookies": res.cookies,
				"logined": True
			}
		except Exception:
			return {
				"name": "",
				"cookies": None,
				"logined": False
			}

	def login_username_fanya(self, account: dict = {"username": "", "password": ""}):
		"""Log into Chaoxing account with username and password via Fanya API.
		:param account: Same as login_username_v2().
		:return: Same as login_username_v3().
		"""
		def encrypt_aes(msg: str = "", key: str = "u2oh6Vu^HWe4_AES"):
			enc = AES_new(key.encode("utf-8"), AES_MODE_CBC, key.encode("utf-8")).encrypt(pad_pkcs7(msg.encode("utf-8"), AES_block_size, "pkcs7"))
			return b64encode(enc).decode("utf-8")
		url = "https://passport2.chaoxing.com/fanyalogin"
		data = {
				"uname": encrypt_aes(msg = account["username"]),
				"password": encrypt_aes(msg = account["password"]),
				"t": True
			}
		try:
			res = self.post(url = url, data = data)
			assert res.json()["status"]
			return {
				"name": "",
				"cookies": res.cookies,
				"logined": True
			}
		except Exception:
			return {
				"name": "",
				"cookies": None,
				"logined": False
			}

	def login_cookies(self, account: dict = {"cookies": None}):
		"""Log into Chaoxing account with cookies.
		:param account: Cookies in dictionary.
		:return: Same as login_username_v2().
		"""
		url = "https://sso.chaoxing.com/apis/login/userLogin4Uname.do"
		try:
			res2 = self.get(url = url, cookies = account["cookies"])
			data = res2.json()
			assert data["result"]
			return {
				"name": data["msg"]["name"],
				"cookies": account["cookies"],
				"logined": True
			}
		except Exception:
			return {
				"name": "",
				"cookies": None,
				"logined": False
			}

	def curriculum_get_curriculum(self, week: str = ""):
		"""Get curriculum.
		:param week: Week number in string, defaulted to the current week.
		:return: Dictionary of class IDs to courses on the curriculum in dictionaries including course IDs, names, classroom locations, teachers and time.
		"""
		def add_lesson(lesson: dict = {}):
			lesson_class_id = str(lesson["classId"])
			lesson = {
				"course_id": str(lesson["courseId"]),
				"name": lesson["name"],
				"location": lesson["location"],
				"teacher": [lesson["teacherName"]],
				"time":[{
					"day": str(lesson["dayOfWeek"]),
					"period": [str(lesson["beginNumber"]), str(lesson["beginNumber"] + lesson["length"] - 1)]
				}]
			}
			if not lesson_class_id in curriculum.keys():
				curriculum[lesson_class_id] = lesson
				return
			if not lesson["time"][0] in curriculum[lesson_class_id]["time"]:
				curriculum[lesson_class_id]["time"].append(lesson["time"][0])
			if not lesson["teacher"][0] in curriculum[lesson_class_id]["teacher"]:
				curriculum[lesson_class_id]["teacher"].append(lesson["teacher"][0])
		url = "https://kb.chaoxing.com/curriculum/getMyLessons"
		params = {
			"week": week
		}
		curriculum = {}
		try:
			res = self.get(url = url, params = params)
			lessons = res.json()["data"]["lessonArray"]
			for lesson in lessons:
				add_lesson(lesson = lesson)
				for conflict in lesson.get("conflictLessons") or {}:
					add_lesson(lesson = conflict)
			return curriculum
		except Exception:
			return {}

	def course_get_courses(self):
		"""Get course IDs corresponding to class IDs. Will only include courses in the root folder.
		:return: Dictionary of class IDs to course IDs.
		"""
		url = "https://mooc1-1.chaoxing.com/visit/courselistdata"
		params = {
			"courseType": 1,
			"courseFolderId": 0,
			"courseFolderSize": 0
		}
		try:
			res = self.get(url = url, params = params)
			courses = {
				row[1]: {
					"course_id": row[0],
					"name": row[2],
					"teacher": row[3].split("，")
				} for row in findall(r"courseId=\"(.*?)\" clazzId=\"(.*?)\".*?title=\"(.*?)\".*?title=\".*?\".*?title=\"(.*?)\"", res.text, DOTALL)
			}
			return courses
		except Exception:
			return {}

	def course_get_course_id(self, course: dict = {"course_id": "", "class_id": ""}):
		"""Get course ID of a course.
		:param course: Course ID (will be filled if not given) and clsss ID in dictionary.
		:return: Course ID corresponding to the class ID.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/class/getClassDetail"
		params = {
			"fid": self.cookies.get("fid") or 0,
			"courseId": "",
			"classId": course["class_id"]
		}
		course_id = course.get("course_id") or self.courses.get(course["class_id"])["course_id"] if self.courses.get(course["class_id"]) else None
		try:
			if not course_id:
				res = self.get(url = url, params = params)
				d = res.json()
				assert d["result"]
				course_id = str(d["data"]["courseid"])
			return course_id or "0"
		except Exception:
			return "0"

	def course_get_location_log(self, course: dict = {"course_id": "", "class_id": ""}):
		"""Get activities of a course.
		:param course: Course ID (will be filled if not given) and class ID in dictionary.
		:return: Dictionary of activity IDs to checkin locations used by the course.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/sign/getLocationLog"
		params = {
			"DB_STRATEGY": "COURSEID",
			"STRATEGY_PARA": "courseId",
			"courseId": self.course_get_course_id(course = course),
			"classId": course["class_id"]
		}
		try:
			res = self.get(url = url, params = params)
			data = res.json()["data"]
			return {
				location["activeid"]: {
					"address": location["address"],
					"latitude": str(location["latitude"]),
					"longitude": str(location["longitude"]),
					"ranged": str(+ (not not location["locationrange"])),
					"range": str(location["locationrange"])
				} for location in data
			}
		except Exception:
			return {}

	def course_get_course_activities(self, course: dict = {"course_id": "", "class_id": ""}):
		"""Get activities of a course.
		:param course: Course ID (will be filled if not given) and class ID in dictionary.
		:return: List of dictionaries of ongoing activities with type, name, activity ID and remaining time.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/active/student/activelist"
		params = {
			"fid": self.cookies.get("fid") or 0,
			"courseId": self.course_get_course_id(course = course),
			"classId": course["class_id"],
			"showNotStartedActive": 0
		}
		try:
			res = self.get(url = url, params = params)
			data = res.json()["data"]["activeList"]
			return [
				{
					"active_id": activity["id"],
					"type": activity.get("otherId"),
					"name": activity["nameOne"],
					"time_left": activity["nameFour"]
				} for activity in data if activity["status"] == 1 and activity.get("otherId") in ("2", "4")
			]
		except Exception:
			return []

	def course_get_activities(self):
		"""Get activities of all courses.
		:return: Dictionary of class IDs to ongoing activities.
		"""
		def wrapper(course: dict = {}):
			nonlocal lock
			lock += 1
			course_activities = self.course_get_course_activities(course = course)
			if course_activities:
				activities[course["class_id"]] = course_activities
			lock -= 1
		step, interval, lock, activities = 32, 0.2, 0, {}
		courses, courses_len = tuple(self.courses.items()), len(self.courses)
		try:
			for j in range(0, courses_len, step):
				for i in range(j, min(j + step, courses_len)):
					Thread(target = wrapper, kwargs = {"course": {"course_id": courses[i][1]["course_id"], "class_id": courses[i][0]}}).start()
				sleep(interval)
			while lock:
				sleep(interval)
			return activities
		except Exception:
			return {}	

	def checkin_get_details(self, activity: dict = {"active_id": ""}):
		"""Get checkin details.
		:param activity: Activity ID in dictionary.
		:return: Checkin details including class ID and MSG code on success.
		"""
		url = "https://mobilelearn.chaoxing.com/newsign/signDetail"
		params = {
			"activePrimaryId": activity["active_id"],
			"type": 1
		}
		try:
			res = self.get(url = url, params = params)
			return {key: str(val) if not val is None else "" for key, val in res.json().items()}
		except Exception:
			return {}

	def checkin_do_analysis(self, activity: dict = {"active_id": ""}):
		"""Do checkin analysis.
		:param activity: Activity ID in dictionary.
		:return: True on success, otherwise False.
		"""
		url1 = "https://mobilelearn.chaoxing.com/pptSign/analysis"
		params1 = {
			"vs": 1,
			"DB_STRATEGY": "RANDOM",
			"aid": activity["active_id"]
		}
		url2 = "https://mobilelearn.chaoxing.com/pptSign/analysis2"
		params2 = {
			"DB_STRATEGY": "RANDOM",
			"code": ""
		}
		try:
			res1 = self.get(url = url1, params = params1)
			params2["code"] = search(r"code=\'\+\'(.*?)\'", res1.text).group(1)
			res2 = self.get(url = url2, params = params2)
			return res2.text == "success"
		except Exception:
			return False

	def checkin_do_presign(self, activity: dict = {"active_id": ""}):
		"""Do checkin pre-sign and get location.
		:param active_id: Activity ID and Class ID in dictionary.
		:return: Checkin location including address, latitude, longitude and range enforcement if not checked-in or 2 if checked-in or 1 if pre-signed on success, otherwise False.
		"""
		url = "https://mobilelearn.chaoxing.com/newsign/preSign"
		params = {
			"courseId": "",
			"classId": "",
			"activePrimaryId": activity["active_id"],
			"general": 1,
			"sys": 1,
			"ls": 1,
			"appType": 15,
			"tid": "",
			"uid": self.cookies["UID"],
			"ut": "s"
		}
		try:
			details = self.checkin_get_details(activity = activity)
			assert details["status"] == "1" and details["isDelete"] == "0"
			params["classId"], params["courseId"] = details["clazzId"], self.course_get_course_id(course = {"class_id": details["clazzId"]})
			res = self.get(url = url, params = params)
			assert res.status_code == 200
			s = search(r"(zsign_success)|\"ifopenAddress\" value=\"(.*?)\".*?(?:\"locationText\" value=\"(.*?)\".*?\"locationLatitude\" value=\"(.*?)\".*?\"locationLongitude\" value=\"(.*?)\".*?\"locationRange\" value=\"(.*?)\".*?\")?", res.text, DOTALL)
			if s:
				if s.group(1) == "zsign_success":
					return 2
				if s.group(1) == "0":
					return 1
				elif s.lastindex == 5:
					return {
						"address": s.group(2),
						"latitude": s.group(3),
						"longitude": s.group(4),
						"ranged": s.group(1),
						"range": s.group(5)
					}
			locations = self.course_get_location_log(course = {"class_id": details["clazzId"]})
			return locations.get(activity["active_id"]) or tuple(locations.values())[0] if locations else 1
		except Exception:
			return 0

	def checkin_checkin_location(self, activity: dict = {"active_id": ""}, location: dict = {"latitude": -1, "longitude": -1, "address": "", "ranged": ""}):
		"""Location checkin.
		:param active_id: Activity ID in dictionary.
		:param location: Address, latitude, longitude and range enforcement in dictionary. Overriden by server-side location. Unused if designated place not enabled.
		:return: True and error message on success, otherwise False and error message.
		"""
		url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
		params = {
			"name": self.name,
			"address": "",
			"activeId": activity["active_id"],
			"uid": self.cookies["UID"],
			"clientip": "",
			"latitude": -1,
			"longitude": -1,
			"fid": self.cookies.get("fid") or 0,
			"appType": 15,
			"ifTiJiao": 0,
			"validate": ""
		}
		try:
			presign = self.checkin_do_presign(activity = activity)
			assert presign, "Presign failure. (" + dumps(activity) + ")"
			if presign == 2:
				return True, "Checkin success. (Already checked in.)"
			assert self.checkin_do_analysis(activity = activity), "Analysis failure. (" + dumps(activity) + ")"
			if type(presign) is dict:
				location = presign
			if location.get("ranged") or location.get("ranged") is None:
				params["address"], params["latitude"], params["longitude"], params["ifTiJiao"] = location["address"], location["latitude"], location["longitude"], 1
			res = self.get(url = url, params = params)
			assert res.text in ("success", "您已签到过了"), "Checkin failure. (" + res.text + ", " + dumps(params) + ")"
			return True, "Checkin success. (" + res.text + ")"
		except Exception as e:
			return False, str(e)

	def checkin_checkin_qrcode(self, activity: dict = {"active_id": "", "enc": ""}, location: dict = {"latitude": -1, "longitude": -1, "address": "", "ranged": ""}):
		"""Qrcode checkin.
		:param active_id: Activity ID and ENC code in dictionary.
		:param location: Same as checkin_checkin_location().
		:return: Same as checkin_checkin_location().
		"""
		url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
		params = {
			"enc": activity["enc"],
			"name": self.name,
			"activeId": activity["active_id"],
			"uid": self.cookies["UID"],
			"clientip": "",
			"location": "",
			"latitude": -1,
			"longitude": -1,
			"fid": self.cookies.get("fid") or 0,
			"appType": 15
		}
		try:
			presign = self.checkin_do_presign(activity = activity)
			assert presign, "Presign failure. (" + dumps(activity) + ")"
			if presign == 2:
				return True, "Checkin success. (Already checked in.)"
			assert self.checkin_do_analysis(activity = activity), "Analysis failure. (" + dumps(activity) + ")"
			if type(presign) is dict:
				location = presign
			if location.get("ranged") or location.get("ranged") is None:
				params["location"] = "{\"result\":1,\"latitude\":" + str(location["latitude"]) + ",\"longitude\":" + str(location["longitude"]) + ",\"address\":\"" + location["address"] + "\"}"
			else:
				params["latitude"], params["longitude"] = location["latitude"], location["longitude"]
			res = self.get(url = url, params = params)
			assert res.text in ("success", "您已签到过了"), "Checkin failure. (" + res.text + ", " + dumps(params) + ")"
			return True, "Checkin success. (" + res.text + ")"
		except Exception as e:
			return False, str(e)

	def checkin_checkin_qrcode_url(self, qr_url: str = "", location: dict = {"latitude": -1, "longitude": -1, "address": "", "ranged": ""}):
		"""Qrcode checkin.
		:param qr_url: URL from qrcode.
		:param location: Same as checkin_checkin_location().
		:return: Same as checkin_checkin_location().
		"""
		try:
			assert "mobilelearn.chaoxing.com/widget/sign/e" in qr_url, "Checkin failure. (Not a checkin URL, " + qr_url + ")"
			params = parse_qs(urlparse(unquote(qr_url)).query)
			return self.checkin_checkin_qrcode(activity = {"active_id": params["id"][0], "enc": params["enc"][0]}, location = location)
		except Exception as e:
			return False, str(e)
