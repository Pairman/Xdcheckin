# -*- coding: utf-8 -*-

from base64 import b64encode
from Crypto.Cipher.AES import new as AES_new, block_size as AES_block_size, MODE_CBC as AES_MODE_CBC
from Crypto.Util.Padding import pad
from datetime import datetime
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
		"chaoxing_course_get_activities_courses_limit": 36,
		"chaoxing_course_get_activities_workers": 16,
		"chaoxing_checkin_location_address_override_maxlen": 0,
		"chaoxing_checkin_location_randomness": True
	}

	def __init__(
		self, username: str = "", password: str = "", cookies = None,
		config: dict = {}
	):
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
		for adapter in self.requests_session.adapters.values():
			adapter._pool_maxsize = 32
		account = {"username": username, "password": password, "cookies": cookies}
		if cookies:
			self.name, self.cookies, self.logined = self.login_cookies(account = account).values()
		if not self.logined and username and password:
			for func in (
				self.login_username_fanya,
				self.login_username_v2,
				self.login_username_v3,
				self.login_username_v5,
				self.login_username_v11,
				self.login_username_mylogin1,
				self.login_username_xxk
			):
				self.name, self.cookies, self.logined = func(account = account).values()
				if self.logined:
					break
		self.courses = self.course_get_courses() if self.logined else {}

	def get(
		self, url: str = "", params: dict = {}, cookies: dict = None,
		headers: dict = None, expire_after: int = 0, **kwargs
	):
		"""Wrapper for requests.get().
		:param url: URL.
		:param params: Parameters.
		:param cookies: Cookies. Overrides existing cookies.
		:param headers: Headers. Overrides existing headers.
		:param **kwargs: Optional arguments.
		:return: Response.
		"""
		try:
			res = self.requests_session.get(
				url = url, params = params,
				cookies = cookies or self.cookies,
				headers = headers or self.config["requests_headers"],
				expire_after = expire_after if self.config["requests_cache_enabled"] else 0,
				**{"verify": False, **kwargs}
			)
			assert res.status_code in (200, 500), res.status_code
		except AssertionError as e:
			res = Response()
			res.status_code, res._content = int(str(e)), b"{}"
		except RequestException:
			res = Response()
			res.status_code, res._content = 404, b"{}"
		finally:
			return res

	def post(
		self, url: str = "", data: dict = {}, cookies: dict = None,
		headers: dict = None, expire_after: int = 0, **kwargs
	):
		"""Wrapper for requests.post().
		:param url: URL.
		:param data: Data.
		:param cookies: Cookies. Overrides existing cookies.
		:param headers: Headers. Overrides existing headers.
		:param **kwargs: Optional arguments.
		:return: Response.
		"""
		try:
			res = self.requests_session.post(
				url = url, data = data,
				cookies = cookies or self.cookies,
				headers = headers or self.config["requests_headers"],
				expire_after = expire_after if self.config["requests_cache_enabled"] else 0,
				**{"verify": False, **kwargs}
			)
			assert res.status_code in (200, 500), res.status_code
		except AssertionError as e:
			res = Response()
			res.status_code, res._content = int(str(e)), b"{}"
		except RequestException:
			res = Response()
			res.status_code, res._content = 404, b"{}"
		finally:
			return res

	def login_username_v2(
		self, account: dict = {"username": "", "password": ""}
	):
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
		if res.status_code == 200 and res.cookies.get("p_auth_token"):
			data = res.json()
			ret.update({
				"name": data["realname"],
				"cookies": res.cookies,
				"logined": True
			})
		return ret

	def login_username_v3(
		self, account: dict = {"username": "", "password": ""}
	):
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

	def login_username_v5(
		self, account: dict = {"username": "", "password": ""}
	):
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
		res = self.post(url = url, data = dumps(data), headers = {
			**self.config["requests_headers"],
			"Content-Type": "application/json;charset=UTF-8"
		})
		if res.status_code == 200 and res.cookies.get("p_auth_token"):
			data = res.json()
			ret.update({
				"name": data["data"]["realname"],
				"cookies": res.cookies,
				"logined": True
			})
		return ret

	def login_username_v11(
		self, account: dict = {"username": "", "password": ""}
	):
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

	def login_username_mylogin1(
		self, account: dict = {"username": "", "password": ""}
	):
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

	def login_username_xxk(
		self, account: dict = {"username": "", "password": ""}
	):
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

	def login_username_fanya(
		self, account: dict = {"username": "", "password": ""}
	):
		"""Log into Chaoxing account with username and password via Fanya API.
		:param account: Same as login_username_v2().
		:return: Same as login_username_v3().
		"""
		def _encrypt_aes(msg: str = "", key: str = "u2oh6Vu^HWe4_AES"):
			enc = AES_new(
				key.encode("utf-8"), AES_MODE_CBC,
				key.encode("utf-8")
			).encrypt(pad(
				msg.encode("utf-8"), AES_block_size, "pkcs7"
			))
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
		if res.status_code == 200:
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
		:param week: Week number. Defaulted to the current week.
		:return: Dictionary of curriculum details and lessons containing course IDs, names, classroom locations, teachers and time.
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
			if not lesson_class_id in curriculum["lessons"]:
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
		res = self.get(url = url, params = params, expire_after = 86400)
		data = res.json().get("data") or {}
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
					"timetable": details["lessonTimeConfigArray"][1 : -1]
				}
			},
			"lessons": {}
		}
		lessons = data.get("lessonArray", [])
		for lesson in lessons:
			_add_lesson(lesson = lesson)
			for conflict in lesson.get("conflictLessons") or {}:
				_add_lesson(lesson = conflict)
		return curriculum

	def course_get_courses(self):
		"""Get all courses in the root folder.
		:return: Dictionary of class IDs to course containing course IDs, names, teachers, status, start and end time.
		"""
		url = "https://mooc1-1.chaoxing.com/visit/courselistdata"
		params = {
			"courseType": 1
		}
		res = self.get(url = url, params = params, expire_after = 86400)
		matches = findall(r"course_(\d+)_(\d+).*?(?:(not-open).*?)?title=\"(.*?)\".*?title.*?title=\"(.*?)\"(?:.*?(\d+-\d+-\d+)～(\d+-\d+-\d+))?", res.text, DOTALL)
		return {
			match[1]: {
				"class_id": match[1],
				"course_id": match[0],
				"name": match[3],
				"teacher": match[4].split("，"),
				"status": int(not bool(match[2])),
				"time_start": match[5],
				"time_end": match[6]
			} for match in matches
		}

	def course_get_course_id(
		self, course: dict = {"course_id": "", "class_id": ""}
	):
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
		course_id = course.get("course_id") or (self.courses.get(course["class_id"]) or {}).get("course_id")
		if not course_id:
			res = self.get(url = url, params = params, expire_after = 86400)
			data = res.json().get("data") or {}
			course_id = str(data.get("courseid") or 0)
		return course_id

	def course_get_location_log(
		self, course: dict = {"course_id": "", "class_id": ""}
	):
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
		res = self.get(url = url, params = params, expire_after = 1800)
		data = res.json().get("data") or {}
		return {
			location["activeid"]: {
				"latitude": location["latitude"],
				"longitude": location["longitude"],
				"address": location["address"],
				"ranged": 1,
				"range": int(location["locationrange"])
			} for location in data
		}

	def course_get_course_activities_v2(
		self, course: dict = {"course_id": "", "class_id": ""}
	):
		"""Get activities of a course via V2 API.
		:param course: Course ID (will be filled if not given) and class ID in dictionary.
		:return: List of dictionaries of ongoing activities with type, name, activity ID, start, end and remaining time.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/active/student/activelist"
		params = {
			"fid": self.cookies.get("fid") or 0,
			"courseId": self.course_get_course_id(course = course),
			"classId": course["class_id"],
			"showNotStartedActive": 0
		}
		res = self.get(url = url, params = params, expire_after = 60)
		data = (res.json().get("data") or {}).get("activeList") or []
		return [
			{
				"active_id": str(activity["id"]),
				"type": activity["otherId"],
				"name": activity["nameOne"],
				"time_start": str(datetime.fromtimestamp(activity["startTime"] // 1000)),
				"time_end": str(datetime.fromtimestamp((activity["endTime"]) // 1000)) if activity["endTime"] else "",
				"time_left": activity["nameFour"]
			} for activity in data if activity["status"] == 1 and activity.get("otherId") in ("2", "4")
		]

	def course_get_course_activities_ppt(
		self, course: dict = {"course_id": "", "class_id": ""}
	):
		"""Get activities of a course via PPT API.
		:param course: Course ID (will be filled if not given) and class ID in dictionary.
		:return: List of dictionaries of ongoing activities with type, name, activity ID, start, end and remaining time.
		"""
		url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist"
		params = {
			"courseId": self.course_get_course_id(course = course),
			"classId": course["class_id"],
			"showNotStartedActive": 0
		}
		res = self.get(url = url, params = params, expire_after = 60)
		data = res.json().get("activeList") or []
		activities = []
		for activity in data:
			if not activity["status"] == 1 or not activity["activeType"] == 2:
				continue
			activity_new = {
				"active_id": str(activity["id"]),
				"name": activity["nameOne"],
				"time_start": str(datetime.fromtimestamp(activity["startTime"] // 1000)),
				"time_left": activity["nameFour"]
			}
			details = self.checkin_get_details(activity = activity_new)
			if not details["otherId"] in (2, 4):
				continue
			activity_new.update({
				"type": str(details["otherId"]),
				"time_end": str(datetime.fromtimestamp(details["endTime"]["time"] // 1000))
			})
			activities.append(activity_new)
		return activities

	def course_get_activities(self):
		"""Get activities of all courses.
		:return: Dictionary of class IDs to ongoing activities.
		"""
		def _get_course_activities(course: dict = {}, func = None):
			course_activities = func(course = course)
			if course_activities:
				activities[course["class_id"]] = course_activities
		activities = {}
		nworkers = self.config["chaoxing_course_get_activities_workers"]
		ncourses = min(self.config["chaoxing_course_get_activities_courses_limit"], len(self.courses))
		courses = tuple(self.courses.values())[: ncourses]
		threads = [
			[
				Thread(target = _get_course_activities, kwargs = {
					"course": courses[j],
					"func": self.course_get_course_activities_v2 if j % 2 else self.course_get_course_activities_ppt
				})
				for j in range(i, min(i + nworkers, ncourses)) if courses[j]["status"]
			]
			for i in range(0, ncourses, nworkers)
		]
		for batch in threads:
			for thread in batch:
				thread.start()
			for thread in batch:
				thread.join()
		return activities

	def checkin_get_details(self, activity: dict = {"active_id": ""}):
		"""Get checkin details.
		:param activity: Activity ID in dictionary.
		:return: Checkin details including class ID on success.
		"""
		url = "https://mobilelearn.chaoxing.com/newsign/signDetail"
		params = {
			"activePrimaryId": activity["active_id"],
			"type": 1
		}
		res = self.get(url = url, params = params, expire_after = 60)
		return res.json()

	def checkin_get_pptactiveinfo(self, activity: dict = {"active_id": ""}):
		"""Get PPT acitvity info.
		:param active_id: Activity ID in dictionary.
		:return: Checkin PPT activity info including class ID and ranged option on success.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/active/getPPTActiveInfo"
		params = {
			"activeId": activity["active_id"]
		}
		res = self.get(url = url, params = params, expire_after = 60)
		return res.json()["data"]

	def checkin_format_location(
		self,
		location: dict = {"latitude": -1, "longitude": -1, "address": ""},
		location_new: dict = {"latitude": -1, "longitude": -1, "address": ""}
	):
		"""Format checkin location.
		:param location: Address, latitude and longitude in dictionary. Used for address override for checkin location.
		:param location_new: Address, latitude and longitude in dictionary. The checkin location to upload.
		:return: Checkin location containing address, latitude, longitude, range and ranged option.
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
		if len(location_new["address"]) < self.config["chaoxing_checkin_location_address_override_maxlen"]:
			location_new["address"] = location["address"]
		return location_new

	def checkin_get_location_log(self, activity: dict = {"active_id": ""}):
		"""Get checkin locations submitted by up to 100 students.
		:param activity: Activity ID in dictionary.
		:return: List of checkin locations containing address, latitude, longitude, range (placeholder) and ranged (placeholder) option.
		"""
		url = "https://mobilelearn.chaoxing.com/pptSign/autoRefeashSignList4Json2"
		params = {
			"activeId": activity["active_id"]
		}
		res = self.get(url = url, params = params)
		data = res.json()["list"]
		return [
			{
				"latitude": location.get("latitude"),
				"longitude": location.get("longitude"),
				"address": location.get("title"),
				"ranged": int(not location.get("latitude") is None),
				"range": 0
			} for location in data
		]

	def checkin_get_location(
		self, activity: dict = {"active_id": ""},
		course: dict ={"course_id": "", "class_id": ""}
	):
		"""Get checkin location from the location log of its corresponding course.
		:param activity: Activity ID in dictionary.
		:param course: Course ID (will be filled if not given) and class ID in dictionary.
		:return: Checkin location containing address, latitude, longitude, range and ranged option.
		"""
		locations = self.course_get_location_log(course = course)
		location = locations.get(activity["active_id"]) or next(iter(locations.values())) if locations else {
				"latitude": -1,
				"longitude": -1,
				"address": "",
				"ranged": 0,
				"range": 0
			}
		return location

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
		res1 = self.get(url = url1, params = params1, expire_after = 1800)
		params2["code"] = search(r"([0-9a-f]{32})", res1.text).group(1)
		res2 = self.get(url = url2, params = params2, expire_after = 1800)
		return res2.text == "success"

	def checkin_do_presign(
		self, activity: dict = {"active_id": ""},
		course: dict ={"course_id": "", "class_id": ""}
	):
		"""Do checkin pre-sign.
		:param activity: Activity ID in dictionary.
		:param course: Course ID (will be filled if not given) and class ID in dictionary.
		:return: 2 if checked-in, otherwise checkin location containing address, latitude, longitude, range and ranged option on success.
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
		match = search(r"ifopenAddress\" value=\"(\d)\"(?:.*?locationText\" value=\"(.*?)\".*?locationLatitude\" value=\"(\d+\.\d+)\".*?locationLongitude\" value=\"(\d+\.\d+)\".*?locationRange\" value=\"(\d+))?|(zsign_success)", res.text, DOTALL)
		if match:
			if match.group(6):
				return 2
			if match.group(1) == "1":
				return {
					"latitude": float(match.group(3) or -1),
					"longitude": float(match.group(4) or -1),
					"address": match.group(2) or "",
					"ranged": int(match.group(1)),
					"range": int(match.group(5) or 0)
				}
		return {
			"latitude": -1,
			"longitude": -1,
			"address": "",
			"ranged": 0,
			"range": 0
		}

	def checkin_checkin_location(
		self, activity: dict = {"active_id": ""},
		location: dict = {"latitude": -1, "longitude": -1, "address": ""}
	):
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
			"fid": self.cookies.get("fid") or 0,
			"appType": 15,
			"ifTiJiao": 0,
			"validate": ""
		}
		try:
			thread_analysis = Thread(target = self.checkin_do_analysis, kwargs = {"activity": activity})
			thread_analysis.start()
			info = self.checkin_get_details(activity = activity)
			assert info["status"] == 1 and not info["isDelete"], "Activity ended or deleted."
			presign = self.checkin_do_presign(activity = activity, course = {"class_id": str(info["clazzId"])})
			assert presign, f"Presign failure. {dumps(activity), dumps(location), dumps(info), dumps(presign)}"
			if presign == 2:
				return True, "Checkin success. (Already checked in.)"
			if presign["ranged"]:
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

	def checkin_checkin_qrcode(
		self, activity: dict = {"active_id": "", "enc": ""},
		location: dict = {"latitude": -1, "longitude": -1, "address": ""}
	):
		"""Qrcode checkin.
		:param active_id: Activity ID and ENC code in dictionary.
		:param location: Same as checkin_checkin_location().
		:return: Same as checkin_checkin_location().
		"""
		def _get_location():
			nonlocal location_new
			location_new = self.checkin_format_location(
				location = location,
				location_new = self.checkin_get_location(activity = activity, course = course)
			)
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
			"fid": self.cookies.get("fid") or 0,
			"appType": 15
		}
		try:
			thread_analysis = Thread(target = self.checkin_do_analysis, kwargs = {"activity": activity})
			thread_analysis.start()
			info = self.checkin_get_pptactiveinfo(activity = activity)
			assert info["status"] == 1 and not info["isdelete"], "Activity ended or deleted."
			course, location_new = {"class_id": str(info["clazzid"])}, {}
			thread_location = Thread(target = _get_location)
			thread_location.start()
			presign = self.checkin_do_presign(activity = activity, course = course)
			assert presign, f"Presign failure. {dumps(activity), dumps(location), dumps(info), presign}"
			if presign == 2:
				return True, "Checkin success. (Already checked in.)"
			if info["ifopenAddress"]:
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

	def checkin_checkin_qrcode_url(
		self, url: str = "",
		location: dict = {"latitude": -1, "longitude": -1, "address": ""}
	):
		"""Qrcode checkin.
		:param url: URL from Qrcode.
		:param location: Same as checkin_checkin_location().
		:return: Same as checkin_checkin_location().
		"""
		try:
			assert "mobilelearn.chaoxing.com/widget/sign/e" in url, f"Checkin failure. {'Invalid URL.', url, dumps(location)}"
			match = search(r"id=(\d+).*?([0-9A-F]{32})", url)
			return self.checkin_checkin_qrcode(activity = {
				"active_id": match.group(1),
				"enc": match.group(2)
			}, location = location)
		except Exception as e:
			return False, str(e)
