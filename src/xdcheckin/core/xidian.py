# -*- coding: utf-8 -*-

from asyncio import create_task as _create_task, gather as _gather
from re import search as _search
from threading import Thread as _Thread
from time import time as _time
from requests import Response as _Response, Session as _Session
from requests.exceptions import RequestException as _RequestException
from xdcheckin.util.encryption import encrypt_aes as _encrypt_aes
from xdcheckin.util.session import CachedSession as _CachedSession

class IDSSession:
	requests_session = secrets = service = logined = None
	config = {
		"requests_headers": {
			"User-Agent":
				"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit"
				"/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 M"
				"obile Safari/537.36"
		}
	}

	def __init__(self, service: str = ""):
		"""Initialize an IDS Session.
		:param service: The SSO service for redirection.
		"""
		if self.logined:
			return
		self.requests_session = _Session()
		self.secrets, self.service = {}, service

	def get(
		self, url: str = "", params: dict = {}, cookies: dict = None,
		headers: dict = None, **kwargs
	):
		"""Wrapper for ``requests.get()``.
		:param url: URL.
		:param params: Parameters.
		:param cookies: Cookies. Overrides existing cookies.
		:param headers: Headers. Overrides existing headers.
		:param **kwargs: Optional arguments.
		:return: Response.
		"""
		try:
			res = self.requests_session.get(
				url = url, params = params, cookies = cookies,
				headers = headers or self.config["requests_headers"],
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
		headers: dict = None, **kwargs
	):
		"""Wrapper for ``requests.post()``.
		:param url: URL.
		:param data: Data.
		:param cookies: Cookies. Overrides existing cookies.
		:param headers: Headers. Overrides existing headers.
		:param **kwargs: Optional arguments.
		:return: Response.
		"""
		try:
			res = self.requests_session.post(
				url = url, data = data, cookies = cookies,
				headers = headers or self.config["requests_headers"],
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

	def login_username_prepare(self):
		"""Prepare verification for username login.
		:return: Base64 encoded captcha background and \
		slider image string.
		"""
		url1 = "https://ids.xidian.edu.cn/authserver/login"
		params1 = {
			"service": self.service
		}
		url2 = "https://ids.xidian.edu.cn/authserver/common/openSliderCaptcha.htl"
		params2 = {
			"_": 0
		}
		ret = {
			"big_img_src": "",
			"small_img_src": ""
		}
		res1 = self.get(url = url1, params = params1)
		if not res1.status_code == 200:
			return ret
		s = _search(
			r"\"pwdEncryptSalt\" value=\"(.*?)\".*?"
			r"\"execution\" value=\"(.*?)\"",
			res1.text
		)
		params2["_"] = str(int(1000 * _time()))
		res2 = self.get(url = url2, params = params2)
		if not res2.status_code == 200:
			return ret
		ret.update({
			"big_img_src": res2.json()["bigImage"],
			"small_img_src": res2.json()["smallImage"]
		})
		self.secrets.update({
			"login_prepare_salt": s.group(1),
			"login_prepare_execution": s.group(2)
		})
		return ret

	def login_username_finish(
		self,
		account: dict = {"username": "", "password": "", "vcode": ""}
	):
		"""Verify and finish username logging in.
		:param account: Username, password and verification \
		code (a.k.a. slider offset).
		:return: Cookies and login state.
		"""
		url1 = "https://ids.xidian.edu.cn/authserver/common/verifySliderCaptcha.htl"
		data1 = {
			"canvasLength": 280,
			"moveLength": account["vcode"]
		}
		ret = {
			"cookies": None,
			"logined": False
		}
		res1 = self.post(url1, data = data1)
		if not res1.status_code == 200 and res1.json()["errorCode"] == 1:
			return ret
		url2 = "https://ids.xidian.edu.cn/authserver/login"
		data2 = {
			"username": account["username"],
			"password": _encrypt_aes(
				msg = account["password"],
				key = self.secrets["login_prepare_salt"].encode("utf-8"),
				iv = b"xidianscriptsxdu",
				pad = lambda msg: 4 * b"xidianscriptsxdu" + msg.encode("utf-8")
			),
			"captcha": "",
			"_eventId": "submit",
			"cllt": "userNameLogin",
			"dllt": "generalLogin",
			"lt": "",
			"execution": self.secrets["login_prepare_execution"],
			"rememberMe": True
		}
		params2 = {
			"service": self.service
		}
		res2 = self.post(url2, data = data2, params = params2)
		if not res2.status_code == 200:
			return ret
		ret.update({
			"cookies": self.requests_session.cookies,
			"logined": True
		})
		return ret

	def login_cookies(self, account: dict = {"cookies": None}):
		"""Login with cookies.
		:param account: Cookies.
		:return: Cookies and login state.
		"""
		url = "http://ids.xidian.edu.cn/authserver/index.do"
		ret = {
			"cookies": None,
			"logined": False
		}
		res = self.get(
			url = url, cookies = account["cookies"],
			allow_redirects = False
		)
		if res.status_code != 302:
			ret.update({
				"cookies": account["cookies"],
				"logined": True
			})
		return ret

class Newesxidian:
	"""XDU exclusive APIs for classroom livestreams.
	"""
	__chaoxing = logined = None

	def __init__(self, chaoxing: None = None):
		"""Create a Newesxidian with ``Chaoxing`` instance.
		:param chaoxing: The ``Chaoxing`` instance.
		:return: None.
		"""
		if not chaoxing.logined or not "fid" in chaoxing.cookies or \
		not chaoxing.cookies["fid"].value == "16820":
			return
		self.logined, self.__chaoxing = True, chaoxing

	async def __aenter__(self):
		return self

	async def __aexit__(self, *args, **kwargs):
		pass

	async def livestream_get_url(self, livestream: dict = {"live_id": ""}):
		"""Get livestream URL.
		:param livesteam: Live ID in dictionary.
		:return: Livestream URL, live ID, device ID and 
		classroom location (``""``).
		URL will fallback to replay URL for non-ongoing live IDs.
		"""
		url = "https://newesxidian.chaoxing.com/live/getViewUrlHls"
		params = {
			"liveId": livestream["live_id"]
		}
		res = await self.__chaoxing.get(
			url = url, params = params, ttl = 86400
		)
		return {
			"url": await res.text(),
			"live_id": livestream["live_id"],
			"device": "",
			"location": ""
		}

	async def livestream_get_live_url(
		self,
		livestream: dict = {"live_id": "", "device": "", "location": ""}
	):
		"""Get livestream URL.
		:param livestream: Live ID (unused if device ID is present), \
		device ID and location (in case device ID is not present) \
		in dictionary.
		:return: Livestream URL, live ID (``""`` if not given), device \
		ID and classroom location (``""`` if device ID not given).
		"""
		url1 = "http://newesxidian.chaoxing.com/live/listSignleCourse"
		params1 = {
			"liveId": livestream.get("live_id") or ""
		}
		url2 = "http://newesxidian.chaoxing.com/live/getViewUrlNoCourseLive"
		params2 = {
			"deviceCode": livestream.get("device") or "",
			"status": 1
		}
		location = livestream.get("location") or ""
		if not livestream.get("device"):
			res1 = self.__chaoxing.get(
				url = url1, params = params1, ttl = 86400
			)
			data = await res1.json() or []
			for lesson in data:
				if str(lesson["id"]) == livestream["live_id"]:
					params2["deviceCode"] = lesson["deviceCode"]
					location = lesson["schoolRoomName"].rstrip()
					break
		res2 = await self.__chaoxing.get(
			url = url2, params = params2, ttl = 86400
		)
		return {
			"url": await res2.text(),
			"live_id": params1["liveId"],
			"device": params2["deviceCode"],
			"location": location
		}

	async def curriculum_get_curriculum(self, week: str = ""):
		"""Get curriculum with livestreams.
		:param week: Week number. Defaulted to the current week.
		:return: Chaoxing curriculum with livestreams for lessons.
		"""
		async def _get_livestream(lesson):
			class_id = str(lesson["teachClazzId"])
			live_id = str(lesson["id"])
			location = str(lesson["place"])
			if not class_id in curriculum["lessons"]:
				return
			if not "livestreams" in curriculum["lessons"][class_id]:
				curriculum["lessons"][class_id]["livestreams"] = []
			livestream = self.livestream_get_live_url(livestream = {
				"live_id": live_id,
				"location": location
			})
			for l in curriculum["lessons"][class_id]["livestreams"]:
				if l["device"] == livestream["device"]:
					return
			curriculum["lessons"][class_id]["livestreams"].append(livestream)
		url = "https://newesxidian.chaoxing.com/frontLive/listStudentCourseLivePage"
		params = {
			"fid": 16820,
			"userId": self.__chaoxing.cookies["UID"].value,
			"termYear": 0,
			"termId": 0,
			"week": week or 0
		}
		curriculum = await self.__chaoxing.curriculum_get_curriculum(
			week = week
		)
		params.update({
			"termYear": curriculum["details"]["year"],
			"termId": curriculum["details"]["semester"],
			"week": week or curriculum["details"]["week"]
		})
		res = await self.__chaoxing.get(
			url = url, params = params, ttl = 86400
		)
		data = await res.json() or []
		await _gather(*[_create_task(
			_get_livestream(lesson)
		) for lesson in data])
		return curriculum
