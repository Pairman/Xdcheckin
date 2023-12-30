# -*- coding: utf-8 -*-

from base64 import b64encode
from Crypto.Cipher.AES import new as AES_new, block_size as AES_block_size, MODE_CBC as AES_MODE_CBC
from re import findall, search, DOTALL
from requests import get, post
from urllib.parse import parse_qs, unquote, urlparse
from urllib3 import disable_warnings

disable_warnings()

class Chaoxing:
	name = uid = fid = cookies = courses = logined = None
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
		self.name, self.uid, self.fid, self.cookies, self.logined = (self.login_cookies if cookies else self.login_username_fanya)(account = {"username": username, "password": password, "cookies": cookies}).values()
		self.courses = self.get_courses() if self.logined else {}

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

	def login_username_v11(self, account: dict = {"username": "", "password": ""}):
		"""Log into Chaoxing account with username and password via V11 API.
		:param account: Username and password in dictionary.
		:return: Name (placeholder), UID, FID, cookies and login state.
		"""
		url = "https://passport2-api.chaoxing.com/v11/loginregister"
		params = {
			"uname": account["username"],
			"code": account["password"],
			"cx_xxt_passport": "json",
			"loginType": 1,
			"roleSelect": True
		}
		try:
			res = self.get(url, params)
			assert res.json()["status"]
			return {
				"name": "",
				"uid": res.cookies["UID"],
				"fid": res.cookies.get("fid") or "",
				"cookies": res.cookies,
				"logined": True
			}
		except Exception:
			return {
				"name": "",
				"uid": "",
				"fid": "",
				"cookies": None,
				"logined": False
			}

	def login_username_fanya(self, account: dict = {"username": "", "password": ""}):
		"""Log into Chaoxing account with username and password via Fanya API.
		:param account: Same as login_username_v11().
		:return: Same as login_username_v11().
		"""
		def encrypt_aes(msg: str = "", key: str = "u2oh6Vu^HWe4_AES"):
			pad_pkcs7 = lambda s: s + (chr(AES_block_size - len(s) % AES_block_size) * (AES_block_size - len(s) % AES_block_size)).encode("utf-8")
			enc = AES_new(key = key.encode("utf-8"), mode = AES_MODE_CBC, iv = key.encode("utf-8")).encrypt(pad_pkcs7(msg.encode("utf-8")))
			return b64encode(enc).decode("utf-8")
		url = "https://passport2.chaoxing.com/fanyalogin"
		data = {
				'fid': -1,
				'uname': encrypt_aes(msg = account["username"]),
				'password': encrypt_aes(msg = account["password"]),
				't': True,
				'validate': "",
				'forbidotherlogin': 0,
				'doubleFactorLogin': 0,
				'independentId': 0,
				'independentNameId': 0
			}
		try:
			res = self.post(url, data)
			assert res.json()["status"]
			return {
				"name": "",
				"uid": res.cookies["UID"],
				"fid": res.cookies.get("fid") or "",
				"cookies": res.cookies,
				"logined": True
			}
		except Exception:
			return {
				"name": "",
				"uid": "",
				"fid": "",
				"cookies": None,
				"logined": False
			}

	def login_cookies(self, account: dict = {"cookies": None}):
		"""Log into Chaoxing account with cookies.
		:param account: Cookies in dictionary.
		:return: Name, UID, FID, cookies and login state.
		"""
		url = "https://sso.chaoxing.com/apis/login/userLogin4Uname.do"
		try:
			res2 = self.get(url, cookies = account["cookies"])
			data = res2.json()
			assert data["result"]
			return {
				"name": data["msg"]["name"],
				"uid": account["cookies"]["UID"],
				"fid": account["cookies"].get("fid") or "",
				"cookies": account["cookies"],
				"logined": True
			}
		except Exception:
			return {
				"name": "",
				"uid": "",
				"fid": "",
				"cookies": None,
				"logined": False
			}

	def get_courses(self):
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
			res = self.get(url, params)
			courses = findall(r"courseId=\"(.*?)\" clazzId=\"(.*?)\".*?title=\"(.*?)\".*?title=\".*?\".*?title=\"(.*?)\"", res.text, DOTALL)
			courses = {
				row[1]: {
					"course_id": row[0],
					"name": row[2],
					"teacher": row[3].split("，")
				} for row in courses
			}
			return courses
		except Exception:
			return {}

	def get_course_course_id(self, course: dict = {"course_id": "", "class_id": ""}):
		"""Get course ID of a course.
		:param course: Course ID (picked if given, otherwise filled later) and clsss ID in dictionary.
		:return: Course ID corresponding to the class ID.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/class/getClassDetail"
		params = {
			"fid": "",
			"courseId": "",
			"classId": course["class_id"]
		}
		course_id = course.get("course_id") or self.courses.get(course["class_id"])["course_id"] if self.courses.get(course["class_id"]) else None
		try:
			if not course_id:
				res = self.get(url, params)
				d = res.json()
				assert d["result"]
				course_id = str(d["data"]["courseid"])
			return course_id or "0"
		except Exception:
			return "0"

	def get_curriculum(self, week: str = ""):
		"""Get curriculum.
		:param week: Week number in string, defaulted to the current week.
		:return: Dictionary of class IDs to courses on the curriculum in dictionaries including course IDs, names, classroom locations, teachers and time.
		"""
		url = "https://kb.chaoxing.com/curriculum/getMyLessons"
		params = {
			"week": week
		}
		try:
			res = self.get(url, params)
			data = res.json()["data"]["lessonArray"]
			curriculum = {}
			def add_lesson(lesson: dict = {}, curriculum = curriculum):
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
			for lesson in data:
				add_lesson(lesson)
				for conflict in lesson.get("conflictLessons") or {}:
					add_lesson(conflict)
			return curriculum
		except Exception:
			return {}

	def get_course_activities(self, course: dict = {"course_id": "", "class_id": ""}):
		"""Get activities of a course.
		:param course: Course ID (will be filled if not given) and class ID in dictionary.
		:return: List of dictionaries of ongoing activities with type, name, activity ID and remaining time.
		"""
		url = "https://mobilelearn.chaoxing.com/v2/apis/active/student/activelist"
		params = {
			"fid": 0,
			"courseId": self.get_course_course_id(course = course),
			"classId": course["class_id"],
			"showNotStartedActive": 0
		}
		try:
			res = self.get(url, params)
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

	def get_activities(self):
		"""Get activities of all courses.
		:param course: Course ID (unnecessary) and class ID in dictionary.
		:return: Dictionary of class IDs to ongoing activities.
		"""
		try:
			activities = {}
			for class_id, course in self.courses.items():
				activity = self.get_course_activities({"course_id": course["course_id"], "class_id": class_id})
				if activity:
					activities[class_id] = activity
			return activities
		except Exception:
			return {}

	def checkin_get_details(self, activity: dict = {"active_id": ""}):
		"""Get checkin details
		:param activity: Activity ID in dictionary.
		:return: Checkin details including class ID and MSG code on success.
		"""
		url = "https://mobilelearn.chaoxing.com/newsign/signDetail"
		params = {
			"activePrimaryId": activity["active_id"],
			"type": 1
		}
		try:
			res = self.get(url, params)
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
			res1 = self.get(url1, params1)
			params2["code"] = search(r"code=\'\+\'(.*?)\'", res1.text).group(1)
			res2 = self.get(url2, params2)
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
			"classId": "",
			"activePrimaryId": activity["active_id"],
			"general": 1,
			"sys": 1,
			"ls": 1,
			"appType": 15,
			"tid": "",
			"uid": self.uid,
			"ut": "s"
		}
		try:
			details = self.checkin_get_details(activity = activity)
			assert details["status"] == "1" and details["isDelete"] == "0"
			params["class_id"] = details["clazzId"]
			res = self.get(url, params)
			assert res.status_code == 200 and not "无此签到活动" in res.text and not "活动已被删除" in res.text
			s = search(r"\"ifopenAddress\" value=\"(.*?)\".*?\"locationText\" value=\"(.*?)\".*?\"locationLatitude\" value=\"(.*?)\".*?\"locationLongitude\" value=\"(.*?)\".*?\"locationRange\" value=\"(.*?)\".*?\"", res.text, DOTALL)
			return {
				"address": s.group(2),
				"latitude": s.group(3),
				"longitude": s.group(4),
				"ranged": s.group(1),
				"range": s.group(5),
			} if s and s.group(1) == "1" else 2 if "zsign_success" in res.text else 1
		except Exception:
			return 0

	def checkin_checkin_location(self, activity: dict = {"active_id": ""}, location: dict = {"latitude": -1, "longitude": -1, "address": "", "ranged": ""}):
		"""Location checkin.
		:param active_id: Activity ID in dictionary.
		:param location: Address, latitude, longitude and range enforcement in dictionary. Overriden by server-side location. Unused if designated place not enabled.
		:return: True on success, otherwise False.
		"""
		try:
			assert self.checkin_do_analysis(activity = activity)
			presign = self.checkin_do_presign(activity = activity)
			assert presign
			if presign == 2:
				return True
			if type(presign) is dict:
				location = presign
			ranged = not not location.get("ranged") or True
			url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
			params = {
				"address": location["address"] if ranged else "",
				"activeId": activity["active_id"],
				"latitude": location["latitude"] if ranged else -1,
				"longitude": location["longitude"] if ranged else -1,
				"fid": 0,
				"appType": 15,
				"ifTiJiao": ranged
			}
			res = self.get(url, params)
			return res.text in ("success", "您已签到过了")
		except Exception:
			return False

	def checkin_checkin_qrcode(self, activity: dict = {"active_id": "", "enc": ""}, location: dict = {"latitude": -1, "longitude": -1, "address": "", "ranged": ""}):
		"""Qrcode checkin.
		:param active_id: Activity ID and ENC code in dictionary.
		:param location: Same as checkin_checkin_location().
		:return: True on success, otherwise False.
		"""
		try:
			assert self.checkin_do_analysis(activity = activity)
			presign = self.checkin_do_presign(activity = activity)
			assert presign
			if presign == 2:
				return True
			if type(presign) is dict:
				location = presign
			ranged = not not location.get("ranged") or True
			url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
			params = {
				"enc": activity["enc"],
				"activeId": activity["active_id"],
				"location": "{\"result\":1,\"latitude\":" + str(location["latitude"]) + ",\"longitude\":" + str(location["longitude"]) + ",\"address\":\"" + location["address"] + "\"}" if ranged else "",
				"latitude": -1 if ranged else location["latitude"],
				"longitude": -1 if ranged else location["longitude"],
				"fid": 0
			}
			res = self.get(url, params)
			return res.text in ("success", "您已签到过了")
		except Exception:
			return False

	def checkin_checkin_qrcode_url(self, qr_url: str = "", location: dict = {"latitude": -1, "longitude": -1, "address": "", "ranged": ""}):
		"""Qrcode checkin.
		:param qr_url: URL from qrcode.
		:param location: Same as checkin_checkin_location().
		:return: True on success, otherwise False.
		"""
		try:
			qr_url.find("mobilelearn.chaoxing.com/widget/sign/e") == -1
			params = parse_qs(urlparse(unquote(qr_url)).query)
			activity = {
				"active_id": params["id"][0],
				"enc": params["enc"][0]
			}
			return self.checkin_checkin_qrcode(activity = activity, location = location)
		except Exception:
			return False
