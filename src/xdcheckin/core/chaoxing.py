# -*- coding: utf-8 -*-

from ast import literal_eval as _literal_eval
from datetime import datetime as _datetime
from json import dumps as _dumps
from random import choice as _choice, uniform as _uniform
from re import findall as _findall, search as _search, DOTALL as _DOTALL
from threading import Thread as _Thread
from requests import Response as _Response
from requests.adapters import HTTPAdapter as _HTTPAdapter
from requests.exceptions import RequestException as _RequestException
from requests_cache.session import CachedSession as _CachedSession
from xdcheckin.util.chaoxing_captcha import generate_secrets as _generate_secrets
from xdcheckin.util.encryption import encrypt_aes as _encrypt_aes

class Chaoxing:
	"""Common Chaoxing APIs.
	"""
	requests_session = name = cookies = courses = logined = None
	config = {
		"requests_headers": {
			"User-Agent":
				"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit"
				"/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 M"
				"obile Safari/537.36 com.chaoxing.mobile/ChaoXi"
				"ngStudy_3_6.1.0_android_phone_906_100"
		},
		"requests_cache_enabled": True,
		"chaoxing_course_get_activities_courses_limit": 32,
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
		:param cookies: Cookies from previous login. 
		Overrides username and password if given.
		:param config: Configurations for the instance.
		:return: None.
		"""
		if self.logined:
			return
		self.config.update(config)
		self.requests_session = _CachedSession(backend = "memory")
		self.requests_session.mount("https://", _HTTPAdapter(pool_maxsize = 32))
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
			res = _Response()
			res.status_code, res._content = int(str(e)), b"{}"
		except _RequestException:
			res = _Response()
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
			res = _Response()
			res.status_code, res._content = int(str(e)), b"{}"
		except _RequestException:
			res = _Response()
			res.status_code, res._content = 404, b"{}"
		finally:
			return res

	def login_username_v2(
		self, account: dict = {"username": "", "password": ""}
	):
		"""Log into Chaoxing account with username and password 
		via V2 API.
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
		"""Log into Chaoxing account with username and password 
		via V3 API.
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
		"""Log into Chaoxing account with username and password 
		via V5 API.
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
		res = self.post(url = url, data = _dumps(data), headers = {
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
		"""Log into Chaoxing account with username and password 
		via V11 API.
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
		"""Log into Chaoxing account with username and password 
		via Mylogin1 API.
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
		"""Log into Chaoxing account with username and password 
		via XXK API.
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
		"""Log into Chaoxing account with username and password 
		via Fanya API.
		:param account: Same as login_username_v2().
		:return: Same as login_username_v3().
		"""
		url = "https://passport2.chaoxing.com/fanyalogin"
		data = {
				"uname": _encrypt_aes(
					msg = account["username"],
					key = b"u2oh6Vu^HWe4_AES",
					iv = b"u2oh6Vu^HWe4_AES"
				),
				"password": _encrypt_aes(
					msg = account["password"],
					key = b"u2oh6Vu^HWe4_AES",
					iv = b"u2oh6Vu^HWe4_AES"
				),
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
		:return: Dictionary of curriculum details and lessons 
		containing course IDs, names, classroom locations, teachers 
		and time.
		"""
		def _add_lesson(lesson: dict = {}):
			lesson_class_id = str(lesson["classId"])
			lesson = {
				"course_id": str(lesson["courseId"]),
				"name": lesson["name"],
				"locations": [lesson["location"]],
				"invite_code": lesson["meetCode"],
				"teachers": [lesson["teacherName"]],
				"times": [{
					"day": str(lesson["dayOfWeek"]),
					"period_begin": str(lesson["beginNumber"]),
					"period_end": str(lesson["beginNumber"] + lesson["length"] - 1)
				}]
			}
			if not lesson_class_id in curriculum["lessons"]:
				curriculum["lessons"][lesson_class_id] = lesson
				return
			if not lesson["locations"][0] in curriculum["lessons"][lesson_class_id]["locations"]:
				curriculum["lessons"][lesson_class_id]["locations"].append(lesson["locations"][0])
			if not lesson["teachers"][0] in curriculum["lessons"][lesson_class_id]["teachers"]:
				curriculum["lessons"][lesson_class_id]["teachers"].append(lesson["teachers"][0])
			if not lesson["times"][0] in curriculum["lessons"][lesson_class_id]["times"]:
				curriculum["lessons"][lesson_class_id]["times"].append(lesson["times"][0])
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
		lessons = data.get("lessonArray") or []
		for lesson in lessons:
			_add_lesson(lesson = lesson)
			for conflict in lesson.get("conflictLessons") or {}:
				_add_lesson(lesson = conflict)
		return curriculum

	def course_get_courses(self):
		"""Get all courses in the root folder.
		:return: Dictionary of class IDs to course containing 
		course IDs, names, teachers, status, start and end time.
		"""
		url = "https://mooc1-1.chaoxing.com/visit/courselistdata"
		params = {
			"courseType": 1
		}
		res = self.get(url = url, params = params, expire_after = 86400)
		matches = _findall(
			r"course_(\d+)_(\d+).*?(?:(not-open).*?)?title="
			r"\"(.*?)\".*?title.*?title=\"(.*?)\""
			r"(?:.*?(\d+-\d+-\d+)～(\d+-\d+-\d+))?",
			res.text, _DOTALL
		)
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
		:param course: Course ID (will be filled if not given) and 
		clsss ID in dictionary.
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
		:param course: Course ID (will be filled if not given) and 
		class ID in dictionary.
		:return: Dictionary of activity IDs to checkin locations 
		used by the course.
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
		:param course: Course ID (will be filled if not given) and 
		class ID in dictionary.
		:return: List of dictionaries of ongoing activities with type, 
		name, activity ID, start, end and remaining time.
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
				"time_start": str(_datetime.fromtimestamp(activity["startTime"] // 1000)),
				"time_end":
					str(_datetime.fromtimestamp(activity["endTime"] // 1000))
					if activity["endTime"] else "",
				"time_left": activity["nameFour"]
			} for activity in data if activity["status"] == 1 and activity.get("otherId") in ("2", "4")
		]

	def course_get_course_activities_ppt(
		self, course: dict = {"course_id": "", "class_id": ""}
	):
		"""Get activities of a course via PPT API.
		:param course: Course ID (will be filled if not given) and 
		class ID in dictionary.
		:return: List of dictionaries of ongoing activities with type, 
		name, activity ID, start, end and remaining time.
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
				"time_start": str(_datetime.fromtimestamp(activity["startTime"] // 1000)),
				"time_left": activity["nameFour"]
			}
			details = self.checkin_get_details(activity = activity_new)
			if not details["otherId"] in (2, 4):
				continue
			activity_new.update({
				"type": str(details["otherId"]),
				"time_end":
					str(_datetime.fromtimestamp(details["endTime"]["time"] // 1000))
					if details["endTime"] else "",
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
				_Thread(target = _get_course_activities, kwargs = {
					"course": courses[j],
					"func": self.course_get_course_activities_v2 if j % 2
						else self.course_get_course_activities_ppt
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
		res = self.get(url = url, params = params, expire_after = 300)
		return res.json()

	def checkin_get_pptactiveinfo(self, activity: dict = {"active_id": ""}):
		"""Get PPT acitvity info.
		:param activity: Activity ID in dictionary.
		:return: Checkin PPT activity info including class ID and 
		ranged option on success.
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
		:param location: Address, latitude and longitude in dictionary. 
		Used for address override for checkin location.
		:param location_new: Address, latitude and longitude 
		in dictionary. The checkin location to upload.
		:return: Checkin location containing address, latitude, 
		longitude, range and ranged option.
		"""
		def _randomness(x: int | float = 0):
			return round(x + _choice((-1, 1)) * _uniform(1, 5) * 0.0001, 6)
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
		:return: List of checkin locations containing address, 
		latitude, longitude, range (placeholder) and 
		ranged (placeholder) option.
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
		"""Get checkin location from the location log of its 
		corresponding course.
		:param activity: Activity ID in dictionary.
		:param course: Course ID (will be filled if not given) and 
		class ID in dictionary.
		:return: Checkin location containing address, latitude, 
		longitude, range and ranged option.
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
		params2["code"] = _search(r"([0-9a-f]{32})", res1.text).group(1)
		res2 = self.get(url = url2, params = params2, expire_after = 1800)
		return res2.text == "success"

	def checkin_get_captcha(self, captcha: dict = {"captcha_id": ""}):
		"""Get CAPTCHA for checkin.
		:param captcha: CAPTCHA ID in dictionary.
		:return: CAPTCHA with CAPTCHA images and token.
		"""
		url1 = "https://captcha.chaoxing.com/captcha/get/conf"
		params1 = {
			"callback": "f",
			"captchaId": captcha["captcha_id"],
			"_": int(_datetime.now().timestamp() * 1000)
		}
		res1 = self.get(url = url1, params = params1, expire_after = 300)
		server_time = _search(r"t\":(\d+)", res1.text).group(1)
		url2 = "https://captcha.chaoxing.com/captcha/get/verification/image"
		params2 = {
			"callback": "f",
			"captchaId": captcha["captcha_id"],
			"captchaKey": "",
			"token": "",
			"type": "slide",
			"version": "1.1.16",
			"referer": "https://mobilelearn.chaoxing.com",
			"_": int(_datetime.now().timestamp() * 1000)
		}
		captcha_new = {
			**captcha,
			"server_time": server_time,
			"type": "slide"
		}
		captcha_key, token = _generate_secrets(captcha = captcha_new)
		params2.update({
			"captchaKey": captcha_key,
			"token": token
		})
		res2 = self.get(url = url2, params = params2)
		data2 = _literal_eval(res2.text[2 : -1])
		return {
			**captcha_new,
			"token": data2["token"],
			"big_img_src": data2["imageVerificationVo"]["shadeImage"],
			"small_img_src": data2["imageVerificationVo"]["cutoutImage"]
		}

	def checkin_submit_captcha(
		self, captcha = {"captcha_id": "", "token": "", "vcode": ""}
	):
		"""Submit and verify CAPTCHA.
		:param captcha: CAPTCHA ID, and verification code (e.g. slider 
		offset) in dictionary.
		:return: CAPTCHA with validation code on success.
		"""
		url = "https://captcha.chaoxing.com/captcha/check/verification/result"
		params = {
			"callback": "f",
			"captchaId": captcha["captcha_id"],
			"token": captcha["token"],
			"textClickArr": f"[{{\"x\": {captcha['vcode']}}}]",
			"type": "slide",
			"coordinate": "[]",
			"version": "1.1.16",
			"runEnv": 10,
			"_": int(_datetime.now().timestamp() * 1000)
		}
		res = self.get(url = url, params = params, headers = {
			**self.config["requests_headers"],
			"Referer": "https://mobilelearn.chaoxing.com"
		})
		return "result\":true" in res.text, {
			**captcha,
			"validate": f"validate_{captcha['captcha_id']}_{captcha['token']}"
		}

	def checkin_do_presign(
		self, activity: dict = {"active_id": ""},
		course: dict ={"course_id": "", "class_id": ""}
	):
		"""Do checkin pre-sign.
		:param activity: Activity ID in dictionary.
		:param course: Course ID (will be filled if not given) and 
		class ID in dictionary.
		:return: Presign state (2 if checked-in and 1 on success), 
		checkin location and CAPTCHA.
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
		location = {
			"latitude": -1,
			"longitude": -1,
			"address": "",
			"ranged": 0,
			"range": 0
		}
		captcha = {
			"captcha_id": ""
		}
		res = self.get(url = url, params = params)
		if res.status_code != 200:
			return 0, location, captcha
		state = 1
		match = _search(
			r"ifopenAddress\" value=\"(\d)\"(?:.*?locationText\" "
			r"value=\"(.*?)\".*?locationLatitude\" value="
			r"\"(\d+\.\d+)\".*?locationLongitude\" value="
			r"\"(\d+\.\d+)\".*?locationRange\" value="
			r"\"(\d+))?.*?captchaId: '([0-9A-Za-z]{32})|"
			r"(zsign_success)",
			res.text, _DOTALL
		)
		if match:
			if match.group(7):
				state = 2
			if match.group(1) == "1":
				location.update({
					"latitude": float(match.group(3) or -1),
					"longitude": float(match.group(4) or -1),
					"address": match.group(2) or "",
					"ranged": int(match.group(1)),
					"range": int(match.group(5) or 0)
				})
			captcha["captcha_id"] = match.group(6)
		return state, location, captcha

	def checkin_do_sign(
		self, activity: dict = {"active_id": "", "type": ""},
		location: dict = {"latitude": -1, "longitude": -1, "address": "", "ranged": 0},
		old_params: dict = {"name": "", "uid": "", "fid": "", "...": "..."}
	):
		"""Do checkin sign.
		:param activity: Activity ID and type in dictionary.
		:param location: Address, latitude, longitude and 
		ranged option in dictionary.
		:param prev_params: Reuse previously returned params. 
		Overrides activity and location.
		:return: Sign state (True on success), success / error message 
		and payload.
		"""
		url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
		params = old_params if old_params.get("activeId") else {
			"name": self.name,
			"uid": self.cookies["_uid"],
			"fid": self.cookies.get("fid") or 0,
			"activeId": activity["active_id"],
			"enc": activity.get("enc") or "",
			"enc2": "",
			"address": "",
			"latitude": -1,
			"longitude": -1,
			"location": "",
			"ifTiJiao": 0,
			"appType": 15,
			"clientip": "",
			"validate": "",
		}
		try:
			if not old_params.get("activeId"):
				if activity["type"] == "4":
					params.update({
						"address": location["address"],
						"latitude": location["latitude"],
						"longitude": location["longitude"],
						"ifTiJiao": location["ranged"]
					})
				elif activity["type"] == "2":
					params.update({
						"location": str(location),
						"ifTiJiao": location["ranged"]
					} if location["ranged"] else {
						"address": location["address"],
						"latitude": location["latitude"],
						"longitude": location["longitude"]
					})
			res = self.get(url = url, params = params)
			assert res.text in ("success", "您已签到过了"), res.text
			return True, {
				"msg": f"Checkin success. ({res.text})",
				"params": params
			}
		except Exception as e:
			if type(e) is AssertionError:
				match = _search(r"validate_([0-9A-Fa-f]{32})", str(e))
				if match:
					params["enc2"] = match.group(1)
				msg = f"Checkin failure. {params, str(e)}"
			else:
				msg = str(e)
			return False, {
				"msg": msg,
				"params": params
			}

	def checkin_checkin_location(
		self, activity: dict = {"active_id": ""},
		location: dict = {"latitude": -1, "longitude": -1, "address": ""}
	):
		"""Location checkin.
		:param activity: Activity ID in dictionary.
		:param location: Address, latitude and longitude in dictionary. 
		Overriden by server-side location if any.
		:return: Checkin state (True on success), message, params and 
		captcha (placeholder if already checked-in or on failure).
		"""
		try:
			thread_analysis = _Thread(target = self.checkin_do_analysis, kwargs = {"activity": activity})
			thread_analysis.start()
			info = self.checkin_get_details(activity = activity)
			assert info["status"] == 1 and not info["isDelete"], "Activity ended or deleted."
			presign = self.checkin_do_presign(activity = activity, course = {"class_id": str(info["clazzId"])})
			assert presign[0], f"Presign failure. {activity, presign}"
			if presign[0] == 2:
				return True, {
					"msg": "Checkin success. (Already checked in.)",
					"params": "",
					"captcha": ""
				}
			location_new = {
				**(
					self.checkin_format_location(location = location, location_new = presign[1])
					if presign[1]["ranged"] else location
				),
				"ranged": presign[1]["ranged"]
			}
			thread_analysis.join()
			result = self.checkin_do_sign(activity = {**activity, "type": "4"}, location = location_new)
			result[1]["captcha"] = presign[2]
			return result
		except Exception as e:
			return False, {
				"msg": str(e),
				"params": {},
				"captcha": {}
			}

	def checkin_checkin_qrcode(
		self, activity: dict = {"active_id": "", "enc": ""},
		location: dict = {"latitude": -1, "longitude": -1, "address": ""}
	):
		"""Qrcode checkin.
		:param activity: Activity ID and ENC code in dictionary.
		:param location: Same as checkin_checkin_location().
		:return: Same as checkin_checkin_location().
		"""
		def _get_location():
			nonlocal location_new
			location_new = self.checkin_format_location(
				location = location,
				location_new = self.checkin_get_location(activity = activity, course = course)
			)
		try:
			thread_analysis = _Thread(target = self.checkin_do_analysis, kwargs = {"activity": activity})
			thread_analysis.start()
			info = self.checkin_get_details(activity = activity)
			assert info["status"] == 1 and not info["isDelete"], "Activity ended or deleted."
			course, location_new = {"class_id": str(info["clazzId"])}, {}
			thread_location = _Thread(target = _get_location)
			thread_location.start()
			presign = self.checkin_do_presign(activity = activity, course = course)
			assert presign[0], f"Presign failure. {activity, presign}"
			if presign[0] == 2:
				return True, {
					"msg": "Checkin success. (Already checked in.)",
					"params": "",
					"captcha": ""
				}
			location_new = {
				**(
					thread_location.join() or
					self.checkin_format_location(location = location, location_new = location_new)
					if presign[1]["ranged"] else location
				),
				"ranged": presign[1]["ranged"]
			}
			thread_analysis.join()
			result = self.checkin_do_sign(activity = {**activity, "type": "2"}, location = location_new)
			result[1]["captcha"] = presign[2]
			return result
		except Exception as e:
			return False, {
				"msg": str(e),
				"params": {},
				"captcha": {}
			}

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
			assert "mobilelearn.chaoxing.com/widget/sign/e" in url, f"Checkin failure. {'Invalid URL.', url}"
			match = _search(r"id=(\d+).*?([0-9A-F]{32})", url)
			return self.checkin_checkin_qrcode(activity = {
				"active_id": match.group(1),
				"enc": match.group(2)
			}, location = location)
		except Exception as e:
			return False, {
				"msg": str(e),
				"params": {},
				"captcha": {}
			}
