# -*- coding: utf-8 -*-

from base64 import b64encode
from Crypto.Cipher.AES import new as AES_new, block_size as AES_block_size, MODE_CBC as AES_MODE_CBC
from Crypto.Util.Padding import pad
from json import dumps
from random import choice, uniform
from re import findall, search, DOTALL
from requests import Response
from requests.exceptions import RequestException
from requests_cache.session import CachedSession
from threading import Thread

class Chaoxing:
	"""Common Chaoxing APIs.
	"""
	requests_session = name = cookies = courses = logined = None
	config = {
		"requests_headers": {
			"User-Agent": "Mozilla/5.0 (Linux; Android 10; K) Apple"
				      "WebKit/537.36 (KHTML, like Gecko) Chrome"
				      "/120.0.0.0 Mobile Safari/537.36 com.chao"
				      "xing.mobile/ChaoXingStudy_3_6.1.0_androi"
				      "d_phone_906_100"
		},
		"requests_cache_enabled": True,
		"chaoxing_course_get_activities_courses_limit": 48,
		"chaoxing_checkin_location_address_override": False,
		"chaoxing_checkin_location_address_override_maxlen": 0,
		"chaoxing_checkin_location_randomness": True
	}

	def __init__(self, username: str = "", password: str = "", cookies = None, config: dict = {}):
		"""Create a Chaoxing instance and login.
		:param username: Chaoxing username. Unused if cookies are given.
		:param password: Chaoxing password. Unused if cookies are given.
		:param cookies: Cookies from previous login. Overrides username and password if given.
		:param config: Configurations for the instance.
		:return: None.
		"""
		if self.logined:
			return
		self.config.update(config)
		self.requests_session = CachedSession(backend = "memory")
		account = {"username": username, "password": password, "cookies": cookies}
		if cookies:
			self.name, self.cookies, self.logined = self.login_cookies(account = account).values()
		if not self.logined and username and password:
			for func in (self.login_username_fanya, self.login_username_v2, self.login_username_v3, self.login_username_v5, self.login_username_v11, self.login_username_mylogin1, self.login_username_xxk):
				self.name, self.cookies, self.logined = func(account = account).values()
				if self.logined:
					break
		self.courses = self.course_get_courses() if self.logined else {}

	def get(self, url: str = "", params: dict = {}, cookies: dict = None, headers: dict = None, verify: bool = False, expire: int = 0, **kwargs):
		"""Wrapper for requests.get().
		:param url: URL.
		:param params: Parameters.
		:param cookies: Cookies. Overrides existing cookies.
		:param headers: Headers. Overrides existing headers.
		:param verify: SSL certificate verification toggle. False by default.
		:param expire: Cache expiration time in seconds. Overriden by config["requests_cache_enabled"].
		:param **kwargs: Optional arguments.
		:return: Response.
		"""
		try:
			res = self.requests_session.get(url, params = params, cookies = cookies or self.cookies, headers = headers or self.config["requests_headers"], verify = False, expire_after = expire if self.config["requests_cache_enabled"] else 0, **kwargs)
			assert res.status_code in (200, 500), res.status_code
		except AssertionError as e:
			res = Response()
			res.status_code, res._content = e, b"{}"
		except RequestException:
			res = Response()
			res.status_code, res._content = 404, b"{}"
		finally:
			return res

	def post(self, url: str = "", data: dict = {}, params: dict = {}, cookies: dict = None, headers: dict = None, verify: bool = False, expire: int = 0, **kwargs):
		"""Wrapper for requests.post().
		:param url: URL.
		:param data: Data.
		:param params: Parameters.
		:param cookies: Cookies. Overrides existing cookies.
		:param headers: Headers. Overrides existing headers.
		:param verify: SSL certificate verification toggle. False by default.
		:param expire: Cache expiration time in seconds. Overriden by config["requests_cache_enabled"].
		:param **kwargs: Optional arguments.
		:return: Response.
		"""
		try:
			res = self.requests_session.post(url, data = data, params = params, cookies = cookies or self.cookies, headers = headers or self.config["requests_headers"], verify = False, expire_after = expire if self.config["requests_cache_enabled"] else 0, **kwargs)
			assert res.status_code in (200, 500), res.status_code
		except AssertionError as e:
			res = Response()
			res.status_code, res._content = e, b"{}"
		except RequestException:
			res = Response()
			res.status_code, res._content = 404, b"{}"
		finally:
			return res

	def login_username_v2(self, account: dict = {"username": "", "password": ""}):
		"""Log into Chaoxing account with username and password via V2 API.
		:param account: Username and password in dictionary.
		:return: Name, cookies and login state.
		"""
		url = "https://passport2.chaoxing.com/api/v2/loginbypwd"
		params = {
			"name": account["username"],
			"pwd": account["password"]
		}
		ret = {
			"name": "",
			"cookies": None,
			"logined": False
		}
		res = self.get(url = url, params = params)
		data = res.json()
		if res.status_code == 200 and res.cookies.get("p_auth_token"):
			ret.update({
				"name": data["realname"],
				"cookies": res.cookies,
				"res": res,
				"logined": True
			})
		return ret

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
		ret = {
			"name": "",
			"cookies": None,
			"logined": False
		}
		res = self.post(url = url, data = data)
		if res.status_code == 200 and res.cookies.get("p_auth_token"):
			ret.update({
				"cookies": res.cookies,
				"logined": True
			})
		return ret

	def login_username_v5(self, account: dict = {"username": "", "password": ""}):
		"""Log into Chaoxing account with username and password via V5 API.
		:param account: Same as login_username_v2().
		:return: Same as login_username_v2().
		"""
		url = "https://v5.chaoxing.com/login/passportLogin"
		data = {
			"userNumber": account["username"],
			"passWord": account["password"]
		}
		ret = {
			"name": "",
			"cookies": None,
			"logined": False
		}
		res = self.post(url = url, data = dumps(data), headers = {**self.config["requests_headers"], **{"Content-Type": "application/json;charset=UTF-8"}})
		d = res.json()
		if res.status_code == 200 and res.cookies.get("p_auth_token"):
			ret.update({
				"name": d["data"]["realname"],
				"cookies": res.cookies,
				"logined": True
			})
		return ret

	def login_username_v11(self, account: dict = {"username": "", "password": ""}):
		"""Log into Chaoxing account with username and password via V11 API.
		:param account: Same as login_username_v2().
		:return: Same as login_username_v3().
		"""
		url = "https://passport2.chaoxing.com/v11/loginregister"
		params = {
			"uname": account["username"],
			"code": account["password"]
		}
		ret = {
			"name": "",
			"cookies": None,
			"logined": False
		}
		res = self.get(url = url, params = params)
		if res.status_code == 200 and res.cookies.get("p_auth_token"):
			ret.update({
				"cookies": res.cookies,
				"logined": True
			})
		return ret

	def login_username_mylogin1(self, account: dict = {"username": "", "password": ""}):
		"""Log into Chaoxing account with username and password via Mylogin1 API.
		:param account: Same as login_username_v2().
		:return: Same as login_username_v3().
		"""
		url = "https://passport2.chaoxing.com/mylogin1"
		data = {
			"msg": account["username"],
			"vercode": account["password"],
			"fid": "undefined",
			"type": 1
		}
		ret = {
			"name": "",
			"cookies": None,
			"logined": False
		}
		res = self.post(url = url, data = data)
		if res.status_code == 200 and res.cookies.get("p_auth_token"):
			ret.update({
				"cookies": res.cookies,
				"logined": True
			})
		return ret

	def login_username_xxk(self, account: dict = {"username": "", "password": ""}):
		"""Log into Chaoxing account with username and password via XXK API.
		:param account: Same as login_username_v2().
		:return: Same as login_username_v3().
		"""
		url = "http://xxk.chaoxing.com/api/front/user/login"
		params = {
			"username": account["username"],
			"password": account["password"],
			"numcode": 0
		}
		ret = {
			"name": "",
			"cookies": None,
			"logined": False
		}
		res = self.get(url = url, params = params)
		if res.status_code == 500 and res.cookies.get("p_auth_token"):
			ret.update({
				"cookies": res.cookies,
				"logined": True
			})
		return ret

	def login_username_fanya(self, account: dict = {"username": "", "password": ""}):
		"""Log into Chaoxing account with username and password via Fanya API.
		:param account: Same as login_username_v2().
		:return: Same as login_username_v3().
		"""
		def _encrypt_aes(msg: str = "", key: str = "u2oh6Vu^HWe4_AES"):
			enc = AES_new(key.encode("utf-8"), AES_MODE_CBC, key.encode("utf-8")).encrypt(pad(msg.encode("utf-8"), AES_block_size, "pkcs7"))
			return b64encode(enc).decode("utf-8")
		url = "https://passport2.chaoxing.com/fanyalogin"
		data = {
				"uname": _encrypt_aes(msg = account["username"]),
				"password": _encrypt_aes(msg = account["password"]),
				"t": True
			}
		ret = {
			"name": "",
			"cookies": None,
			"logined": False
		}
		res = self.post(url = url, data = data)
		if res.status_code == 200 and res.cookies.get("p_auth_token"):
			ret.update({
				"cookies": res.cookies,
				"logined": True
			})
		return ret

	def login_cookies(self, account: dict = {"cookies": None}):
		"""Log into Chaoxing account with cookies.
		:param account: Cookies in dictionary.
		:return: Same as login_username_v2().
		"""
		url = "https://sso.chaoxing.com/apis/login/userLogin4Uname.do"
		ret = {
			"name": "",
			"cookies": None,
			"logined": False
		}
		res = self.get(url = url, cookies = account["cookies"])
		data = res.json()
		if data["result"]:
			ret.update({
				"name": data["msg"]["name"],
				"cookies": account["cookies"],
				"logined": True
			})
		return ret

	def curriculum_get_curriculum(self, week: str = ""):
		"""Get curriculum.
		:param week: Week number in string. Defaulted to the current week.
		:return: Dictionary of curriculum details and lessons with class IDs to courses on the curriculum in dictionaries including course IDs, names, classroom locations, teachers and time.
		"""
		def _add_lesson(lesson: dict = {}):
			lesson_class_id = str(lesson["classId"])
			lesson = {
				"course_id": str(lesson["courseId"]),
				"name": lesson["name"],
				"location": lesson["location"],
				"invite_code": lesson["meetCode"],
				"teacher": [lesson["teacherName"]],
				"time":[{
					"day": str(lesson["dayOfWeek"]),
					"period_begin": str(lesson["beginNumber"]),
					"period_end": str(lesson["beginNumber"] + lesson["length"] - 1)
				}]
			}
			if not lesson_class_id in curriculum["lessons"].keys():
				curriculum["lessons"][lesson_class_id] = lesson
				return
			if not lesson["teacher"][0] in curriculum["lessons"][lesson_class_id]["teacher"]:
				curriculum["lessons"][lesson_class_id]["teacher"].append(lesson["teacher"][0])
			if not lesson["time"][0] in curriculum["lessons"][lesson_class_id]["time"]:
				curriculum["lessons"][lesson_class_id]["time"].append(lesson["time"][0])
		url = "https://kb.chaoxing.com/curriculum/getMyLessons"
		params = {
			"week": week
		}
		res = self.get(url = url, params = params, expire = 86400)
		data = res.json().get("data", {})
		details = data["curriculum"]
		curriculum = {
			"details": {
				"year": str(details["schoolYear"]),
				"semester": str(details["semester"]),
				"week": str(details["currentWeek"]),
				"week_real": str(details["realCurrentWeek"]),
				"week_max": str(details["maxWeek"]),
				"time": {
					"period_max": str(details["maxLength"]),
					"timetable": details["lessonTimeConfigArray"][1: -1]
				}
			},
			"lessons": {}
		}
		lessons = data.get("lessonArray", [])
		for lesson in lessons:
			_add_lesson(lesson = lesson)
			for conflict in lesson.get("conflictLessons", {}):
				_add_lesson(lesson = conflict)
		return curriculum

	def course_get_courses(self):
		"""Get all courses in the root folder.
		:return: Dictionary of class IDs to course including course IDs, names and teachers.
		"""
		url = "https://mooc1-1.chaoxing.com/visit/courselistdata"
		params = {
			"courseType": 1
		}
		res = self.get(url = url, params = params, expire = 86400)
		return {
			row[1]: {
				"course_id": row[0],
				"name": row[2],
				"teacher": row[3].split("，")
			} for row in findall(r"courseId=\"(.*?)\" clazzId=\"(.*?)\".*?title=\"(.*?)\".*?title=\".*?\".*?title=\"(.*?)\"", res.text, DOTALL)
		}

	def course_get_course_id(self, course: dict = {"course_id": "", "class_id": ""}):
		"""Get course ID of a course.
		:param course: Course ID (will be filled if not given) and clsss ID in dictionary.
		:return: Course ID corresponding to the class ID.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/class/getClassDetail"
		params = {
			"fid": self.cookies.get("fid", 0),
			"courseId": "",
			"classId": course["class_id"]
		}
		course_id = course.get("course_id", self.courses.get(course["class_id"], {}).get("course_id"))
		if not course_id:
			res = self.get(url = url, params = params, expire = 86400)
			data = res.json().get("data", {})
			course_id = str(data.get("courseid", 0))
		return course_id

	def course_get_location_log(self, course: dict = {"course_id": "", "class_id": ""}):
		"""Get checkin location history of a course.
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
		res = self.get(url = url, params = params, expire = 600)
		data = res.json().get("data", {})
		return {
			location["activeid"]: {
				"latitude": location["latitude"],
				"longitude": location["longitude"],
				"address": location["address"],
				"ranged": int(location["locationrange"]),
				"range": int(location["locationrange"])
			} for location in data
		}

	def course_get_course_activities(self, course: dict = {"course_id": "", "class_id": ""}):
		"""Get activities of a course.
		:param course: Course ID (will be filled if not given) and class ID in dictionary.
		:return: List of dictionaries of ongoing activities with type, name, activity ID and remaining time.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/active/student/activelist"
		params = {
			"fid": self.cookies.get("fid", 0),
			"courseId": self.course_get_course_id(course = course),
			"classId": course["class_id"],
			"showNotStartedActive": 0
		}
		res = self.get(url = url, params = params, expire = 60)
		data = res.json().get("data", {}).get("activeList", [])
		return [
			{
				"active_id": activity["id"],
				"type": activity["otherId"],
				"name": activity["nameOne"],
				"time_left": activity["nameFour"]
			} for activity in data if activity["status"] == 1 and activity.get("otherId") in ("2", "4")
		]

	def course_get_activities(self):
		"""Get activities of all courses.
		:return: Dictionary of class IDs to ongoing activities.
		"""
		def _get_course_activities_wrapper(course: dict = {}):
			course_activities = self.course_get_course_activities(course = course)
			if course_activities:
				activities[course["class_id"]] = course_activities
		activities = {}
		threads = tuple(Thread(target = _get_course_activities_wrapper, kwargs = {"course": {"course_id": course[1]["course_id"], "class_id": course[0]}}) for course in tuple(self.courses.items())[: self.config["chaoxing_course_get_activities_courses_limit"]])
		tuple(thread.start() for thread in threads)
		tuple(thread.join() for thread in threads)
		return activities

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
		res = self.get(url = url, params = params, expire = 60)
		return {key: str(val) if not val is None else "" for key, val in res.json().items()}

	def checkin_get_pptactiveinfo(self, activity: dict = {"active_id": ""}):
		"""Get PPT acitvity info.
		:param active_id: Activity ID in dictionary.
		:return: Checkin PPT activity info including ranged option and Qrcode refreshing optiion on success.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/active/getPPTActiveInfo"
		params = {
			"activeId": activity["active_id"]
		}
		res = self.get(url = url, params = params, expire = 60)
		return {key: str(val) if not val is None else "" for key, val in res.json().get("data", {}).items()}

	def checkin_format_location(self, location: dict = {"latitude": -1, "longitude": -1, "address": ""}, location_new: dict = {"latitude": -1, "longitude": -1, "address": ""}):
		"""Format checkin location.
		:param activity: Activity ID in dictionary.
		:param location: Address, latitude and longitude in dictionary. Used for address override for checkin location.
		:param location_new: Address, latitude and longitude in dictionary. The checkin location to upload.
		:return: Checkin location including address, latitude, longitude, range and ranged option.
		"""
		def _randomness(x: int | float = 0):
			return round(x + choice((-1, 1)) * uniform(1, 5) * 0.0001, 6)
		location_new = {
			"ranged": 0,
			"range": 0,
			**location_new
		}
		if self.config["chaoxing_checkin_location_randomness"]:
			location_new.update({
				"latitude": _randomness(location_new["latitude"]),
				"longitude": _randomness(location_new["longitude"])
			})
		if self.config["chaoxing_checkin_location_address_override"] and len(location["address"]) <= self.config["chaoxing_checkin_location_address_override_maxlen"] or len(location["address"]):
			location_new["address"] = location["address"]
		return location_new

	def checkin_get_location(self, activity: dict = {"active_id": ""}, location: dict = {"latitude": -1, "longitude": -1, "address": ""}, course: dict ={"course_id": "", "class_id": ""}):
		"""Get checkin location from the location log of its corresponding course.
		:param activity: Activity ID in dictionary.
		:param location: Address, latitude and longitude in dictionary. Used for address override for checkin location.
		:param course: Course ID (will be filled if not given) and class ID in dictionary.
		:return: Checkin location including address, latitude, longitude, range and ranged option.
		"""
		locations = self.course_get_location_log(course = course)
		location_new = locations.get(activity["active_id"], tuple(locations.values())[0]) if locations else location
		return self.checkin_format_location(location = location, location_new = location_new)

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
		res1 = self.get(url = url1, params = params1, expire = 600)
		params2["code"] = search(r"code=\'\+\'(.*?)\'", res1.text).group(1)
		res2 = self.get(url = url2, params = params2, expire = 600)
		return res2.text == "success"

	def checkin_do_presign(self, activity: dict = {"active_id": ""}, course: dict ={"course_id": "", "class_id": ""}):
		"""Do checkin pre-sign.
		:param activity: Activity ID in dictionary.
		:param course: Course ID (will be filled if not given) and class ID in dictionary.
		:return: 2 if checked-in and checkin location (including address, latitude, longitude, range and ranged option) on success.
		"""
		url = "https://mobilelearn.chaoxing.com/newsign/preSign"
		params = {
			"courseId": self.course_get_course_id(course = course),
			"classId": course["class_id"],
			"activePrimaryId": activity["active_id"],
			"general": 1,
			"sys": 1,
			"ls": 1,
			"appType": 15,
			"tid": "",
			"uid": self.cookies["UID"],
			"ut": "s"
		}
		res = self.get(url = url, params = params)
		if res.status_code != 200:
			return 0
		s = search(r"ifopenAddress\" value=\"(.*?)\"(?:.*?locationText\" value=\"(.*?)\".*?locationLatitude\" value=\"(.*?)\".*?locationLongitude\" value=\"(.*?)\".*?locationRange\" value=\"(.*?)米)?|(zsign_success)", res.text, DOTALL)
		if s:
			if s.group(6):
				return 2
			if s.group(1) == "1":
				return {
					"latitude": float(s.group(3) or -1),
					"longitude": float(s.group(4) or -1),
					"address": s.group(2) or "",
					"ranged": int(s.group(1)),
					"range": int(s.group(5) or 0)
				}
		return {
			"latitude": -1,
			"longitude": -1,
			"address": "",
			"ranged": 0,
			"range": 0
		}

	def checkin_checkin_location(self, activity: dict = {"active_id": ""}, location: dict = {"latitude": -1, "longitude": -1, "address": ""}):
		"""Location checkin.
		:param active_id: Activity ID in dictionary.
		:param location: Address, latitude and longitude in dictionary. Overriden by server-side location if any.
		:return: True and error message on success, otherwise False and error message.
		"""
		url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
		params = {
			"name": self.name,
			"address": "",
			"activeId": activity["active_id"],
			"uid": self.cookies["_uid"],
			"clientip": "",
			"latitude": -1,
			"longitude": -1,
			"fid": self.cookies.get("fid", 0),
			"appType": 15,
			"ifTiJiao": 0,
			"validate": ""
		}
		try:
			thread_analysis = Thread(target = self.checkin_do_analysis, kwargs = {"activity": activity})
			thread_analysis.start()
			info = self.checkin_get_pptactiveinfo(activity = activity)
			assert info["status"] == "1" and info["isdelete"] == "0", "Activity ended or deleted."
			presign = self.checkin_do_presign(activity = activity, course = {"class_id": info["clazzid"]})
			assert presign, f"Presign failure. {dumps(activity), dumps(location), dumps(info), dumps(presign)}"
			if presign == 2:
				return True, "Checkin success. (Already checked in.)"
			if presign["ranged"] == 1:
				location_new = self.checkin_format_location(location = location, location_new = presign)
				ranged = 1
			else:
				location_new = location
				ranged = 0
			params.update({
				"address": location_new["address"],
				"latitude": location_new["latitude"],
				"longitude": location_new["longitude"],
				"ifTiJiao": ranged
			})
			thread_analysis.join()
			res = self.get(url = url, params = params)
			assert res.text in ("success", "您已签到过了"), f"Checkin failure. {dumps(activity), dumps(location), dumps(info), dumps(presign), dumps(location_new), dumps(params), res.text}"
			return True, f"Checkin success. ({res.text})"
		except Exception as e:
			return False, str(e)

	def checkin_checkin_qrcode(self, activity: dict = {"active_id": "", "enc": ""}, location: dict = {"latitude": -1, "longitude": -1, "address": ""}):
		"""Qrcode checkin.
		:param active_id: Activity ID and ENC code in dictionary.
		:param location: Same as checkin_checkin_location().
		:return: Same as checkin_checkin_location().
		"""
		def _get_location():
			nonlocal location_new
			location_new = self.checkin_get_location(activity = activity, location = location, course = course)
		url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
		params = {
			"enc": activity["enc"],
			"name": self.name,
			"activeId": activity["active_id"],
			"uid": self.cookies["_uid"],
			"clientip": "",
			"location": "",
			"latitude": -1,
			"longitude": -1,
			"fid": self.cookies.get("fid", 0),
			"appType": 15
		}
		try:
			thread_analysis = Thread(target = self.checkin_do_analysis, kwargs = {"activity": activity})
			thread_analysis.start()
			info = self.checkin_get_pptactiveinfo(activity = activity)
			assert info["status"] == "1" and info["isdelete"] == "0", "Activity ended or deleted."
			course, ranged = {"class_id": info["clazzid"]}, info["ifopenAddress"]
			if ranged == "1":
				location_new, thread_location = {}, Thread(target = _get_location)
				thread_location.start()
			presign = self.checkin_do_presign(activity = activity, course = course)
			assert presign, f"Presign failure. {dumps(activity), dumps(location), dumps(info), presign}"
			if presign == 2:
				return True, "Checkin success. (Already checked in.)"
			if ranged == "1":
				thread_location.join()
				params["location"] = str(location_new)
			else:
				location_new = location
				params.update({
					"latitude": location_new["latitude"],
					"longitude": location_new["longitude"]
				})
			thread_analysis.join()
			res = self.get(url = url, params = params)
			assert res.text in ("success", "您已签到过了"), f"Checkin failure. {dumps(activity), dumps(location), dumps(info), dumps(presign), dumps(location_new), dumps(params), res.text}"
			return True, f"Checkin success. ({res.text})"
		except Exception as e:
			return False, str(e)

	def checkin_checkin_qrcode_url(self, url: str = "", location: dict = {"latitude": -1, "longitude": -1, "address": ""}):
		"""Qrcode checkin.
		:param url: URL from Qrcode.
		:param location: Same as checkin_checkin_location().
		:return: Same as checkin_checkin_location().
		"""
		try:
			assert "mobilelearn.chaoxing.com/widget/sign/e" in url, f"Checkin failure. {'Invalid URL.', url, dumps(location)}"
			s = search(r"id=(.*?)&.*?enc=(.*?)&", url)
			return self.checkin_checkin_qrcode(activity = {"active_id": s.group(1), "enc": s.group(2)}, location = location)
		except Exception as e:
			return False, str(e)
