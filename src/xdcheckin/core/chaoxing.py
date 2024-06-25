# -*- coding: utf-8 -*-

__all__ = ("Chaoxing", )

from asyncio import (
	create_task as _create_task, gather as _gather, Semaphore as _Semaphore
)
from json import loads as _loads
from math import trunc as _trunc
from random import uniform as _uniform
from re import compile as _compile, DOTALL as _DOTALL
from time import time as _time
from xdcheckin.util.captcha import (
	chaoxing_captcha_get_checksum as _chaoxing_captcha_get_checksum
)
from xdcheckin.util.encryption import encrypt_aes as _encrypt_aes
from xdcheckin.util.session import CachedSession as _CachedSession
from xdcheckin.util.time import strftime as _strftime

_Chaoxing_login_username_yz_regex = _compile(
	r"enc.*?([0-9a-f]{32})", _DOTALL
)

_Chaoxing_course_get_courses_regex1 = _compile(
	r"Client\('(\d+)','(.*?)','(\d+).*?color3\" title=\"(.*?)\".*?\n"
	r"(?:[^\n]*?(\d+-\d+-\d+)～(\d+-\d+-\d+))?", _DOTALL
)

_Chaoxing_course_get_courses_regex2 = _compile(r", |,|，|、")

_Chaoxing_captcha_get_captcha_regex = _compile(r"t\":(\d+)")

_Chaoxing_checkin_do_analysis_regex = _compile(r"([0-9a-f]{32})")

_Chaoxing_checkin_do_presign_regex = _compile(
	r"ifopenAddress\" value=\"(\d)\"(?:.*?locationText\" value=\"(.*?)\""
	r".*?locationLatitude\" value=\"(\d+\.\d+)\".*?locationLongitude\" "
	r"value=\"(\d+\.\d+)\".*?locationRange\" value=\"(\d+))?.*?"
	r"captchaId: '([0-9A-Za-z]{32})|(zsign_success)", _DOTALL
)

_Chaoxing_checkin_do_sign_regex = _compile(r"validate_([0-9A-Fa-f]{32})")

_Chaoxing_checkin_checkin_qrcode_url_regex = _compile(
	r"id=(\d+).*?([0-9A-F]{32})"
)

class Chaoxing:
	"""Common Chaoxing APIs.
	"""
	__config = {
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
	__async_ctxmgr = __session = __account = __cookies = None
	__courses = {}
	__fid = __uid = "0"
	__logged_in = False

	def __init__(
		self, username: str = "", password: str = "", cookies = {},
		config: dict = {}
	):
		"""Create a Chaoxing instance and login.
		:param username: Chaoxing username. \
		Unused if ``cookies`` is given.
		:param password: Chaoxing password. \
		Unused if ``cookies`` is given.
		:param cookies: Cookies from previous login. Overrides \
		``username`` and ``password`` if given.
		:param config: Configurations.
		:return: None.
		"""
		if not self.__async_ctxmgr is None:
			return
		assert (username and password) or cookies
		assert type(config) is dict
		self.__config.update(config)
		self.__session = _CachedSession(
			headers = self.__config["requests_headers"],
			cache_enabled = self.__config["requests_cache_enabled"]
		)
		self.__account = {
			"username": username, "password": password,
			"cookies": cookies
		}

	async def __aenter__(self):
		if not self.__async_ctxmgr is None:
			return self
		self.__async_ctxmgr = True
		await self.__session.__aenter__()
		username, password, cookies = self.__account.values()
		if cookies:
			self.name, cookies, self.__logged_in = (
				await self.login_cookies(
					account = self.__account
				)
			).values()
		funcs = (
			self.login_username_fanya, self.login_username_v3,
			self.login_username_v25, self.login_username_v2,
			self.login_username_v11, self.login_username_xxk,
			self.login_username_mylogin1, self.login_username_yz
		)
		if not self.__logged_in and username and password:
			for f in funcs:
				self.name, cookies, self.__logged_in = (await f(
					account = self.__account
				)).values()
				if self.__logged_in:
					break
		if self.__logged_in:
			if "fid" in cookies:
				self.__fid = cookies["fid"].value
			self.__cookies = self.__session.cookies = cookies
			self.__uid = cookies["UID"].value
			self.__courses = await self.course_get_courses()
		return self

	async def __aexit__(self, *args, **kwargs):
		if not self.__async_ctxmgr:
			return
		await self.__session.__aexit__(*args, **kwargs)
		self.__account = None
		self.__fid = self.__uid = "0"
		self.__courses = {}
		self.__logged_in = False
		self.__async_ctxmgr = False

	@property
	def logged_in(self):
		return self.__logged_in

	@property
	def fid(self):
		return self.__fid

	@property
	def uid(self):
		return self.__uid

	@property
	def courses(self):
		return self.__courses

	@property
	def cookies(self):
		return self.__cookies

	async def get(self, *args, **kwargs):
		return await self.__session.get(*args, **kwargs)

	async def post(self, *args, **kwargs):
		return await self.__session.post(*args, **kwargs)

	async def captcha_get_captcha(self, captcha: dict = {"captcha_id": ""}):
		"""Get CAPTCHA for checkin.
		:param captcha: CAPTCHA ID and type.
		:return: CAPTCHA images and token.
		"""
		url1 = "https://captcha.chaoxing.com/captcha/get/conf"
		params1 = {
			"callback": "f", "captchaId": captcha["captcha_id"],
			"_": _trunc(_time() * 1000)
		}
		res1 = await self.__session.get(url = url1, params = params1)
		captcha = {
			**captcha, "type": "slide", "server_time":
			_Chaoxing_captcha_get_captcha_regex.search(
				await res1.text()
			)[1]
		}
		captcha_key, token = _chaoxing_captcha_get_checksum(captcha = captcha)
		url2 = "https://captcha.chaoxing.com/captcha/get/verification/image"
		params2 = {
			"callback": "f",
			"captchaId": captcha["captcha_id"],
			"captchaKey": captcha_key,
			"token": token,
			"type": "slide", "version": "1.1.16",
			"referer": "https://mobilelearn.chaoxing.com",
			"_": _trunc(_time() * 1000)
		}
		res2 = await self.__session.get(url = url2, params = params2)
		data2 = _loads((await res2.text())[2 : -1])
		captcha.update({
			"token": data2["token"],
			"big_img_src":
			data2["imageVerificationVo"]["shadeImage"],
			"small_img_src":
			data2["imageVerificationVo"]["cutoutImage"]
		})
		return captcha

	async def captcha_submit_captcha(
		self, captcha = {"captcha_id": "", "token": "", "vcode": ""}
	):
		"""Submit and verify CAPTCHA.
		:param captcha: CAPTCHA ID, and verification code \
		(i.e. slider offset).
		:return: CAPTCHA with validation code on success.
		"""
		url = "https://captcha.chaoxing.com/captcha/check/verification/result"
		params = {
			"callback": "f",
			"captchaId": captcha["captcha_id"],
			"token": captcha["token"],
			"textClickArr": f"[{{\"x\": {captcha['vcode']}}}]",
			"type": "slide", "coordinate": "[]",
			"version": "1.1.16", "runEnv": 10,
			"_": _trunc(_time() * 1000)
		}
		res = await self.__session.get(
			url = url, params = params, headers = {
				**self.__session.headers,
				"Referer": "https://mobilelearn.chaoxing.com"
			}
		)
		return "result\":true" in await res.text(), {
			**captcha, "validate":
			f"validate_{captcha['captcha_id']}_{captcha['token']}"
		}

	async def login_username_v2(
		self, account: dict = {"username": "", "password": ""}
	):
		"""Log into Chaoxing account with username and password \
		via V2 API.
		:param account: Username and password in dictionary.
		:return: Name, cookies and login state.
		"""
		url = "https://passport2.chaoxing.com/api/v2/loginbypwd"
		params = {
			"name": account["username"], "pwd": account["password"]
		}
		ret = {"name": "", "cookies": None, "logged_in": False}
		res = await self.__session.get(
			url = url, params = params, allow_redirects = False
		)
		if res.status == 200 and "p_auth_token" in res.cookies:
			data = await res.json(content_type = None)
			ret.update({
				"name": data["realname"],
				"cookies": res.cookies, "logged_in": True
			})
		return ret

	async def login_username_v3(
		self, account: dict = {"username": "", "password": ""}
	):
		"""Log into Chaoxing account with username and password \
		via V3 API.
		:param account: Same as ``login_username_v2()``.
		:return: Name (``""``), cookies and login state.
		"""
		url = "http://v3.chaoxing.com/vLogin"
		data = {
			"userNumber": account["username"],
			"passWord": account["password"]
		}
		ret = {"name": "", "cookies": None, "logged_in": False}
		res = await self.__session.post(
			url = url, data = data, allow_redirects = False
		)
		if res.status == 200 and "p_auth_token" in res.cookies:
			ret.update({"cookies": res.cookies, "logged_in": True})
		return ret

	async def login_username_v11(
		self, account: dict = {"username": "", "password": ""}
	):
		"""Log into Chaoxing account with username and password \
		via V11 API.
		:param account: Same as ``login_username_v2()``.
		:return: Same as ``login_username_v3()``.
		"""
		url = "https://passport2.chaoxing.com/v11/loginregister"
		data = {
			"uname": account["username"],
			"code": account["password"]
		}
		ret = {"name": "", "cookies": None, "logged_in": False}
		res = await self.__session.post(
			url = url, data = data, allow_redirects = False
		)
		if res.status == 200 and "p_auth_token" in res.cookies:
			ret.update({"cookies": res.cookies, "logged_in": True})
		return ret

	async def login_username_v25(
		self, account: dict = {"username": "", "password": ""}
	):
		"""Log into Chaoxing account with username and password \
		via V25 API.
		:param account: Same as ``login_username_v2()``.
		:return: Same as ``login_username_v3()``.
		"""
		url = "https://v25.chaoxing.com/login"
		data = {"name": account["username"], "pwd": account["password"]}
		ret = {"name": "", "cookies": None, "logged_in": False}
		res = await self.__session.post(
			url = url, data = data, allow_redirects = False
		)
		if res.status == 200 and "p_auth_token" in res.cookies:
			ret.update({"cookies": res.cookies, "logged_in": True})
		return ret

	async def login_username_xxk(
		self, account: dict = {"username": "", "password": ""}
	):
		"""Log into Chaoxing account with username and password \
		via XXK API.
		:param account: Same as ``login_username_v2()``.
		:return: Same as ``login_username_v3()``.
		"""
		url = "http://xxk.chaoxing.com/api/front/user/login"
		data = {
			"username": account["username"], 
			"password": account["password"], "numcode": 0
		}
		ret = {"name": "", "cookies": None, "logged_in": False}
		res = await self.__session.post(
			url = url, data = data, allow_redirects = False
		)
		if "p_auth_token" in res.cookies:
			ret.update({"cookies": res.cookies, "logged_in": True})
		return ret

	async def login_username_mylogin1(
		self, account: dict = {"username": "", "password": ""}
	):
		"""Log into Chaoxing account with username and password \
		via Mylogin1 API.
		:param account: Same as ``login_username_v2()``.
		:return: Same as ``login_username_v3()``.
		"""
		url = "https://passport2.chaoxing.com/mylogin1"
		data = {
			"fid": "undefined", "msg": account["username"], 
			"vercode": account["password"], "type": 1
		}
		ret = {"name": "", "cookies": None, "logged_in": False}
		res = await self.__session.post(
			url = url, data = data, allow_redirects = False
		)
		if res.status == 200 and "p_auth_token" in res.cookies:
			ret.update({"cookies": res.cookies, "logged_in": True})
		return ret

	async def login_username_fanya(
		self, account: dict = {"username": "", "password": ""}
	):
		"""Log into Chaoxing account with username and password \
		via Fanya API.
		:param account: Same as ``login_username_v2()``.
		:return: Same as ``login_username_v3()``.
		"""
		url = "https://passport2.chaoxing.com/fanyalogin"
		data = {
			"uname": _encrypt_aes(
				msg = account["username"],
				key = b"u2oh6Vu^HWe4_AES",
				iv = b"u2oh6Vu^HWe4_AES"
			), "password": _encrypt_aes(
				msg = account["password"],
				key = b"u2oh6Vu^HWe4_AES",
				iv = b"u2oh6Vu^HWe4_AES"
			), "t": True
		}
		ret = {"name": "", "cookies": None, "logged_in": False}
		res = await self.__session.post(
			url = url, data = data, allow_redirects = False
		)
		if res.status == 200 and "p_auth_token" in res.cookies:
			ret.update({"cookies": res.cookies, "logged_in": True})
		return ret

	async def login_username_yz(
		self, account: dict = {"username": "", "password": ""}
	):
		"""Log into Chaoxing account with username and password \
		via Yunzhou API.
		:param account: Same as ``login_username_v2()``.
		:return: Same as ``login_username_v3()``.
		"""
		ret = {"name": "", "cookies": None, "logged_in": False}
		url1 = "https://yz.chaoxing.com"
		res1 = await self.__session.get(url1, allow_redirects = False)
		if res1.status != 200:
			return ret
		match = _Chaoxing_login_username_yz_regex.search(
			await res1.text()
		)
		if not match:
			return ret
		url2 = "https://yz.chaoxing.com/login6"
		data2 = {
			"enc": match[1], "uname": account["username"],
			"password": account["password"]
		}
		res = await self.__session.post(
			url2, data2, allow_redirects = False
		)
		if "p_auth_token" in res.cookies:
			ret.update({"cookies": res.cookies, "logged_in": True})
		return ret


	async def login_cookies(self, account: dict = {"cookies": None}):
		"""Log into Chaoxing account with cookies.
		:param account: Cookies in dictionary.
		:return: Same as ``login_username_v2()``.
		"""
		url = "https://sso.chaoxing.com/apis/login/userLogin4Uname.do"
		ret = {"name": "", "cookies": None, "logged_in": False}
		res = await self.__session.get(
			url = url, cookies = account["cookies"],
			allow_redirects = False
		)
		if res.status == 200:
			data = await res.json(content_type = None)
			if data["result"]:
				ret.update({
					"name": data["msg"]["name"],
					"cookies": res.cookies,
					"logged_in": True
				})
		return ret

	async def curriculum_get_curriculum(self, week: str = ""):
		"""Get curriculum.
		:param week: Week number. Defaulted to the current week.
		:return: Dictionary of curriculum details and lessons \
		containing course IDs, names, classroom locations, teachers \
		and time.
		"""
		def _add_lesson(lesson):
			class_id = f"{lesson['classId']}"
			lesson = {
				"class_id": class_id,
				"course_id": f"{lesson['courseId']}",
				"name": lesson["name"],
				"locations": [lesson["location"]],
				"invite_code": lesson["meetCode"],
				"teachers": [lesson["teacherName"]],
				"times": [{
					"day": f"{lesson['dayOfWeek']}",
					"period_begin":
					f"{lesson['beginNumber']}",
					"period_end": f"""{
						lesson['beginNumber'] +
						lesson['length'] - 1
					}"""
				}]
			}
			if not class_id in curriculum["lessons"]:
				curriculum["lessons"][class_id] = lesson
				return
			_lesson = curriculum["lessons"][class_id]
			if not lesson["locations"][0] in _lesson["locations"]:
				_lesson["locations"].append(
					lesson["locations"][0]
				)
			if not lesson["teachers"][0] in _lesson["teachers"]:
				_lesson["teachers"].append(
					lesson["teachers"][0]
				)
			if not lesson["times"][0] in _lesson["times"]:
				_lesson["times"].append(lesson["times"][0])
		url = "https://kb.chaoxing.com/curriculum/getMyLessons"
		params = {
			"week": week
		}
		res = await self.__session.get(
			url = url, params = params, ttl = 86400
		)
		data = (await res.json()).get("data")
		details = data["curriculum"]
		curriculum = {
			"details": {
				"year": f"{details['schoolYear']}",
				"semester": f"{details['semester']}",
				"week": f"{details['currentWeek']}",
				"week_real": f"{details['realCurrentWeek']}",
				"week_max": f"{details['maxWeek']}",
				"time": {
					"period_max": f"{details['maxLength']}",
					"timetable":
					details["lessonTimeConfigArray"][1 : -1]
				}
			}, "lessons": {}
		}
		lessons = data.get("lessonArray") or []
		for lesson in lessons:
			_add_lesson(lesson = lesson)
			for conflict in lesson.get("conflictLessons") or {}:
				_add_lesson(lesson = conflict)
		return curriculum

	async def course_get_courses(self):
		"""Get all courses in the root folder.
		:return: Dictionary of class IDs to course containing \
		course IDs, names, teachers, status, start and end time.
		"""
		url = "https://mooc2-ans.chaoxing.com/visit/courselistdata"
		params = {"courseType": 1}
		res = await self.__session.get(
			url = url, params = params, ttl = 86400
		)
		text = (await res.text())
		pos = text.index("isState")
		active = _Chaoxing_course_get_courses_regex1.findall(
			text, endpos = pos
		)
		ended = _Chaoxing_course_get_courses_regex1.findall(
			text, pos = pos
		)
		courses = {}
		def _fill_courses(matches, status):
			for match in matches:
				teachers = \
				_Chaoxing_course_get_courses_regex2.split(
					match[3]
				)
				courses[match[2]] = {
					"class_id": match[2],
					"course_id": match[0],
					"name": match[1],
					"teachers": teachers,
					"status": status,
					"time_start": match[4],
					"time_end": match[5]
				}
		_fill_courses(active, 1)
		_fill_courses(ended, 0)
		return courses

	async def course_get_course_id(
		self, course: dict = {"course_id": "", "class_id": ""}
	):
		"""Get course ID of a course.
		:param course: Course ID (optional) and clsss ID.
		:return: Course ID corresponding to the class ID.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/class/getClassDetail"
		params = {
			"fid": self.__fid, "courseId": "",
			"classId": course["class_id"]
		}
		course_id = course.get("course_id") or self.__courses.get(
			course["class_id"], {}
		).get("course_id")
		if not course_id:
			res = await self.__session.get(
				url = url, params = params, ttl = 86400
			)
			data = (await res.json()).get('data', {})
			course_id = f"{data.get('courseid', 0)}"
		return course_id or "0"

	async def course_get_location_log(
		self, course: dict = {"course_id": "", "class_id": ""}
	):
		"""Get checkin location history of a course.
		:param course: Course ID (optional) and class ID.
		:return: Dictionary of activity IDs to checkin locations \
		used by the course.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/sign/getLocationLog"
		params = {
			"DB_STRATEGY": "COURSEID", "STRATEGY_PARA": "courseId",
			"courseId":
			await self.course_get_course_id(course = course),
			"classId": course["class_id"]
		}
		res = await self.__session.get(
			url = url, params = params, ttl = 1800
		)
		data = (await res.json()).get("data") or []
		return {
			location["activeid"]: {
				"latitude": location["latitude"],
				"longitude": location["longitude"],
				"address": location["address"],
				"ranged": 1,
				"range": int(location["locationrange"])
			} for location in data
		}

	async def course_get_course_activities_v2(
		self, course: dict = {"course_id": "", "class_id": ""}
	):
		"""Get activities of a course via V2 API.
		:param course: Course ID (optional) and class ID.
		:return: List of ongoing activities with type, name, \
		activity ID, start, end and remaining time.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/active/student/activelist"
		params = {
			"fid": self.__fid, "courseId":
			await self.course_get_course_id(course = course),
			"classId": course["class_id"], "showNotStartedActive": 0
		}
		res = await self.__session.get(
			url = url, params = params, ttl = 60
		)
		data = ((await res.json()).get("data") or {}).get(
			"activeList"
		) or []
		return [
			{
				"active_id": f"{activity['id']}",
				"type": activity["otherId"],
				"name": activity["nameOne"],
				"time_start":
				_strftime(activity["startTime"] // 1000),
				"time_end":
				_strftime(activity["endTime"] // 1000)
				if activity["endTime"] else "",
				"time_left": activity["nameFour"]
			} for activity in data if (
				activity["status"] == 1 and
				activity.get("otherId") in ("2", "4")
			)
		]

	async def course_get_course_activities_ppt(
		self, course: dict = {"course_id": "", "class_id": ""}
	):
		"""Get activities of a course via PPT API.
		:param course: Course ID (optional) and class ID.
		:return: List of ongoing activities with type, name, \
		activity ID, start, end and remaining time.
		"""
		url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist"
		params = {
			"courseId":
			await self.course_get_course_id(course = course),
			"classId": course["class_id"],
			"showNotStartedActive": 0
		}
		res = await self.__session.get(
			url = url, params = params, ttl = 60
		)
		data = (await res.json(
			content_type = None
		)).get("activeList") or []
		if not data:
			return
		all_details = {}
		_sem = _Semaphore(self.__config[
			"chaoxing_course_get_activities_workers"
		])
		async def _get_details(active_id):
			a = {"active_id": f"{active_id}"}
			async with _sem:
				all_details[active_id] = \
				await self.checkin_get_details(activity = a)
		await _gather(*(
			_get_details(activity["id"]) for activity in data
			if activity["status"] == 1 and
			activity["activeType"] == 2
		))
		activities = []
		for activity in data:
			if (
				activity["status"] != 1 or
				activity["activeType"] != 2
			):
				continue
			details = all_details[activity["id"]]
			if not details["otherId"] in (2, 4):
				continue
			activities.append({
				"active_id": f"{activity['id']}",
				"name": activity["nameOne"],
				"time_start":
				_strftime(activity["startTime"] // 1000),
				"time_left": activity["nameFour"],
				"type": f"{details['otherId']}",
				"time_end": _strftime(
					details["endTime"]["time"] // 1000
				) if details["endTime"] else ""
			})
		return activities

	async def course_get_activities(self):
		"""Get activities of all courses.
		:return: Dictionary of Class IDs to ongoing activities.
		"""
		courses = tuple(
			self.__courses.values()
		)[: self.__config["chaoxing_course_get_activities_courses_limit"]]
		activities = {}
		_sem = _Semaphore(
			self.__config["chaoxing_course_get_activities_workers"]
		)
		async def _worker(func, course):
			async with _sem:
				course_activities = await func(course = course)
			if course_activities:
				activities[course["class_id"]] = course_activities
		await _gather(*(_worker(
			self.course_get_course_activities_v2 if i % 2
			else self.course_get_course_activities_ppt, course
		) for i, course in enumerate(courses) if course["status"]))
		return activities

	async def checkin_get_details(self, activity: dict = {"active_id": ""}):
		"""Get checkin details.
		:param activity: Activity ID.
		:return: Checkin details including class ID on success.
		"""
		url = "https://mobilelearn.chaoxing.com/newsign/signDetail"
		params = {"activePrimaryId": activity["active_id"], "type": 1}
		res = await self.__session.get(
			url = url, params = params, ttl = 300
		)
		return await res.json(content_type = None)

	async def checkin_get_pptactiveinfo(
		self, activity: dict = {"active_id": ""}
	):
		"""Get checkin PPT activity information.
		:param activity: Activity ID.
		:return: Checkin PPT activity details including class ID \
		and ranged flag on success.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/active/getPPTActiveInfo"
		params = {"activeId": activity["active_id"]}
		res = await self.__session.get(
			url = url, params = params, ttl = 60
		)
		return (await res.json()).get("data") or {}

	def checkin_format_location(
		self,
		location: dict = {"latitude": -1, "longitude": -1, "address": ""},
		new_location: dict = {"latitude": -1, "longitude": -1, "address": ""}
	):
		"""Format checkin location.
		:param location: Address, latitude and longitude. \
		Used for address override for checkin location.
		:param location_new: Address, latitude and longitude. \
		The checkin location to upload.
		:return: Checkin location containing address, latitude, \
		longitude, range and ranged flag.
		"""
		new_location = {"ranged": 0, "range": 0, **new_location}
		_rand = lambda x: round(x - 0.0005 + _uniform(0, 0.001), 6)
		if self.__config["chaoxing_checkin_location_randomness"]:
			new_location.update({
				"latitude": _rand(new_location["latitude"]),
				"longitude": _rand(new_location["longitude"])
			})
		if len(new_location["address"]) < self.__config[
			"chaoxing_checkin_location_address_override_maxlen"
		]:
			new_location["address"] = location["address"]
		return new_location

	async def checkin_get_location(
		self, activity: dict = {"active_id": ""},
		course: dict ={"course_id": "", "class_id": ""}
	):
		"""Get checkin location from the location log of its \
		corresponding course.
		:param activity: Activity ID in dictionary.
		:param course: Course ID (optional) and class ID.
		:return: Checkin location containing address, latitude, \
		longitude, range and ranged flag.
		"""
		locations = await self.course_get_location_log(course = course)
		return locations.get(
			activity["active_id"], next(iter(locations.values()))
		) if locations else {
			"latitude": -1, "longitude": -1, "address": "",
			"ranged": 0, "range": 0
		}

	async def checkin_do_analysis(self, activity: dict = {"active_id": ""}):
		"""Do checkin analysis.
		:param activity: Activity ID in dictionary.
		:return: True on success, otherwise False.
		"""
		url1 = "https://mobilelearn.chaoxing.com/pptSign/analysis"
		params1 = {
			"vs": 1, "DB_STRATEGY": "RANDOM",
			"aid": activity["active_id"]
		}
		res1 = await self.__session.get(
			url = url1, params = params1, ttl = 1800
		)
		if res1.status != 200:
			return False
		url2 = "https://mobilelearn.chaoxing.com/pptSign/analysis2"
		params2 = {
			"code": _Chaoxing_checkin_do_analysis_regex.search(
				await res1.text()
			)[1], "DB_STRATEGY": "RANDOM"
		}
		res2 = await self.__session.get(
			url = url2, params = params2, ttl = 1800
		)
		return await res2.text() == "success"

	async def checkin_do_presign(
		self, activity: dict = {"active_id": ""},
		course: dict ={"course_id": "", "class_id": ""}
	):
		"""Do checkin pre-sign.
		:param activity: Activity ID in dictionary.
		:param course: Course ID (optional) and class ID.
		:return: Presign state (2 if checked-in or 1 on success), \
		checkin location and CAPTCHA.
		"""
		url = "https://mobilelearn.chaoxing.com/newsign/preSign"
		params = {
			"courseId":
			await self.course_get_course_id(course = course),
			"classId": course["class_id"],
			"activePrimaryId": activity["active_id"],
			"general": 1, "sys": 1, "ls": 1, "appType": 15,
			"tid": "", "uid": self.__uid, "ut": "s"
		}
		location = {
			"latitude": -1, "longitude": -1, "address": "",
			"ranged": 0, "range": 0
		}
		captcha = {"captcha_id": ""}
		res = await self.__session.get(url = url, params = params)
		if res.status != 200:
			return 0, location, captcha
		state = 1
		match = _Chaoxing_checkin_do_presign_regex.search(
			await res.text()
		)
		if match:
			if match[7]:
				state = 2
			if match[1] == "1":
				location = {
					"latitude": float(match[3] or -1),
					"longitude": float(match[4] or -1),
					"address": match[2] or "",
					"ranged": int(match[1]),
					"range": int(match[5] or 0)
				}
			captcha["captcha_id"] = match[6]
		return state, location, captcha

	async def checkin_do_sign(
		self, activity: dict = {"active_id": "", "type": ""},
		location: dict = {"latitude": -1, "longitude": -1, "address": "", "ranged": 0},
		old_params: dict = {"name": "", "uid": "", "fid": "", "...": "..."}
	):
		"""Do checkin sign.
		:param activity: Activity ID and type in dictionary.
		:param location: Address, latitude, longitude and ranged flag.
		:param old_params: Reuse previous parameters. \
		Overrides activity and location if given.
		:return: Sign state (True on success), message and parameters.
		"""
		url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
		if old_params.get("activeId"):
			params = old_params
		else:
			params = {
				"name": "",
				"uid": self.__uid, "fid": self.__fid,
				"activeId": activity["active_id"],
				"enc": activity.get("enc", ""),
				"enc2": "", "address": "", "latitude": -1,
				"longitude": -1, "location": "", "ifTiJiao": 0,
				"appType": 15, "clientip": "", "validate": ""
			}
			if activity["type"] == "4":
				params.update({
					"address": location["address"],
					"latitude": location["latitude"],
					"longitude": location["longitude"],
					"ifTiJiao": location["ranged"]
				})
			elif activity["type"] == "2":
				params.update({
					"location": f"{location}",
					"ifTiJiao": location["ranged"]
				} if location["ranged"] else {
					"address": location["address"],
					"latitude": location["latitude"],
					"longitude": location["longitude"]
				})
		status = False
		res = await self.__session.get(url = url, params = params)
		text = await res.text()
		if text in ("success", "您已签到过了"):
			status = True
			msg = f"Checkin success. ({text})"
		else:
			match = _Chaoxing_checkin_do_sign_regex.search(text)
			if match:
				params["enc2"] = match[1]
			msg = f"Checkin failure. ({text})"
		return status, {"msg": msg, "params": params}

	async def checkin_checkin_location(
		self, activity: dict = {"active_id": ""},
		location: dict = {"latitude": -1, "longitude": -1, "address": ""}
	):
		"""Location checkin.
		:param activity: Activity ID in dictionary.
		:param location: Address, latitude and longitude. \
		Overriden by server-side location if any.
		:return: Checkin state (True on success), message, \
		parameters and captcha (``{}`` if checked-in or failed).
		"""
		try:
			_analyze = _create_task(self.checkin_do_analysis(
				activity = activity
			))
			info = await self.checkin_get_details(
				activity = activity
			)
			assert (
				info["status"] == 1 and not info["isDelete"]
			), "Activity ended or deleted."
			course = {"class_id": f"{info['clazzId']}"}
			presign = await self.checkin_do_presign(
				activity = activity, course = course
			)
			assert (
				presign[0]
			), f"Presign failure. {activity, presign}"
			if presign[0] == 2:
				return True, {
					"msg":
					"Checkin success. (Already checked in.)",
					"params": {}, "captcha": {}
				}
			location = self.checkin_format_location(
				location = location, new_location = presign[1]
			) if presign[1]["ranged"] else {**location, "ranged": 0}
			await _analyze
			result = await self.checkin_do_sign(
				activity = {**activity, "type": "4"},
				location = location
			)
			result[1]["captcha"] = presign[2]
			return result
		except Exception as e:
			return False, {
				"msg": f"{e}", "params": {}, "captcha": {}
			}

	async def checkin_checkin_qrcode(
		self, activity: dict = {"active_id": "", "enc": ""},
		location: dict = {"latitude": -1, "longitude": -1, "address": ""}
	):
		"""Qrcode checkin.
		:param activity: Activity ID and ENC in dictionary.
		:param location: Same as ``checkin_checkin_location()``.
		:return: Same as ``checkin_checkin_location()``.
		"""
		try:
			_analyze = _create_task(self.checkin_do_analysis(
				activity = activity
			))
			info = await self.checkin_get_details(
				activity = activity
			)
			assert (
				info["status"] == 1 and not info["isDelete"]
			), "Activity ended or deleted."
			course = {"class_id": f"{info['clazzId']}"}
			_locate = _create_task(self.checkin_get_location(
				activity = activity, course = course
			))
			presign = await self.checkin_do_presign(
				activity = activity, course = course
			)
			assert (
				presign[0]
			), f"Presign failure. {activity, presign}"
			if presign[0] == 2:
				return True, {
					"msg":
					"Checkin success. (Already checked in.)",
					"params": {}, "captcha": {}
				}
			if presign[1]["ranged"]:
				location = self.checkin_format_location(
					location = location,
					new_location = await _locate
				)
			else:
				location["ranged"] = 0
			await _analyze
			result = await self.checkin_do_sign(
				activity = {**activity, "type": "2"},
				location = location
			)
			result[1]["captcha"] = presign[2]
			return result
		except Exception as e:
			return False, {
				"msg": f"{e}", "params": {}, "captcha": {}
			}

	async def checkin_checkin_qrcode_url(
		self, url: str = "",
		location: dict = {"latitude": -1, "longitude": -1, "address": ""}
	):
		"""Qrcode checkin.
		:param url: URL from Qrcode.
		:param location: Same as ``checkin_checkin_location()``.
		:return: Same as ``checkin_checkin_location()``.
		"""
		try:
			assert (
				"mobilelearn.chaoxing.com/widget/sign/e" in url
			), f"Checkin failure. {'Invalid URL.', url}"
			match = \
			_Chaoxing_checkin_checkin_qrcode_url_regex.search(url)
			return await self.checkin_checkin_qrcode(activity = {
				"active_id": match[1], "enc": match[2]
			}, location = location)
		except Exception as e:
			return False, {
				"msg": f"{e}", "params": {}, "captcha": {}
			}
