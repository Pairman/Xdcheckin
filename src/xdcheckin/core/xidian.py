# -*- coding: utf-8 -*-

__all__ = ("IDSSession", "Newesxidian")

from asyncio import create_task as _create_task, gather as _gather
from math import trunc as _trunc
from re import compile as _compile
from time import time as _time
from xdcheckin.core.chaoxing import Chaoxing as _Chaoxing
from xdcheckin.util.encryption import encrypt_aes as _encrypt_aes
from xdcheckin.util.session import CachedSession as _CachedSession

_IDSSession_login_username_prepare_regex = _compile(
	r"\"pwdEncryptSalt\" value=\"(.*?)\".*?\"execution\" value=\"(.*?)\""
)

class IDSSession:
	__config = {
		"requests_headers": {
			"User-Agent":
				"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit"
				"/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 M"
				"obile Safari/537.36"
		},
		"requests_cache_enabled": True
	}
	__async_ctxmgr = __session = __secrets = __service = None

	def __init__(
			self, service: str = "", type = "userNameLogin",
			config: dict = {}
		):
		"""Initialize an IDS Session.

		:param service: The SSO service for redirection.
		:param type: Login type. ``"userNameLogin"`` by default for \
		username and ``"dynamicLogin"`` for phone number.
		:param config: Configurations.
		:return: None
		"""
		if not self.__async_ctxmgr is None:
			return
		self.__config.update(config)
		self.__session = _CachedSession(
			headers = self.__config["requests_headers"],
			cache_enabled = self.__config["requests_cache_enabled"]
		)
		self.__secrets, self.__service = {"login_type": type}, service

	async def __aenter__(self):
		if not self.__async_ctxmgr is None:
			return self
		self.__async_ctxmgr = True
		await self.__session.__aenter__()
		return self

	async def __aexit__(self, *args, **kwargs):
		if not self.__async_ctxmgr:
			return
		await self.__session.__aexit__(*args, **kwargs)
		self.__secrets = None
		self.__async_ctxmgr = False

	async def get(self, *args, **kwargs):
		return await self.__session.get(*args, **kwargs)

	async def post(self, *args, **kwargs):
		return await self.__session.post(*args, **kwargs)

	async def captcha_get_captcha(self):
		"""Get CAPTCHA for checkin.

		:return: CAPTCHA images and token.
		"""
		url = "https://ids.xidian.edu.cn/authserver/common/openSliderCaptcha.htl"
		params = {"_": f"{_trunc(1000 * _time())}"}
		res = await self.__session.get(url, params = params)
		data = await res.json()
		return {
			"big_img_src": data["bigImage"],
			"small_img_src": data["smallImage"]
		}

	async def captcha_submit_captcha(self, captcha = {"vcode": ""}):
		"""Submit and verify CAPTCHA.

		:param captcha: Verification code (i.e. slider offset).
		:return: True on success.
		"""
		url = "https://ids.xidian.edu.cn/authserver/common/verifySliderCaptcha.htl"
		data = {"canvasLength": 280, "moveLength": captcha["vcode"]}
		res = await self.__session.post(url, data = data)
		return not not (res.status == 200 and (
			await res.json()
		)["errorMsg"] == "success")

	async def login_prepare(self):
		"""Prepare to log into IDS with username and password.

		:return: True on success.
		"""
		url = "https://ids.xidian.edu.cn/authserver/login"
		params = {
			"service": self.__service,
			"type": self.__secrets["login_type"]
		}
		res = await self.__session.get(url, params = params)
		if res.status != 200:
			return False
		s = _IDSSession_login_username_prepare_regex.search(
			await res.text()
		)
		self.__secrets.update({
			"login_type": self.__secrets["login_type"],
			"login_salt": s[1], "login_execution": s[2]
		})
		return True

	async def login_username_finish(
		self,
		account: dict = {"username": "", "password": ""}
	):
		"""Finish logging into IDS with username and password.

		:param account: Username and password.
		:return: Cookies and login state.
		"""
		password = _encrypt_aes(
			msg = account["password"],
			key = self.__secrets["login_salt"].encode("utf-8"),
			iv = 16 * b" ",
			pad = lambda msg: 64 * b" " + msg.encode("utf-8")
		)
		url = "https://ids.xidian.edu.cn/authserver/login"
		data = {
			"username": account["username"], "password": password,
			"captcha": "", "_eventId": "submit",
			"cllt": self.__secrets["login_type"],
			"dllt": "generalLogin", "lt": "", "rememberMe": True,
			"execution": self.__secrets["login_execution"]
		}
		params = {"service": self.__service}
		res = await self.__session.post(
			url, data = data, params = params
		)
		ret = {"cookies": None, "logged_in": False}
		if res.status == 200:
			ret.update({
				"cookies": self.__session.session_cookies,
				"logged_in": "CASTGC" in
				self.__session.session_cookies.filter_cookies(
					"https://ids.xidian.edu.cn/authserver"
				)
			})
		return ret

	async def login_dynamic_send_code(
		self, account: dict = {"username": ""}
	):
		"""Send dynamic code for logging into IDS.

		:param account: Username (i.e. phone number).
		:return: True on success.
		"""
		url = "https://ids.xidian.edu.cn/authserver/dynamicCode/getDynamicCode.htl"
		data = {"mobile": account["username"], "captcha": ""}
		res = await self.__session.post(url, data = data)
		return not not (res.status == 200 and (
			await res.json(content_type = None)
		)["code"] in ("success", "timeExpire"))

	async def login_dynamic_finish(
		self, account: dict = {"username": "", "password": ""}
	):
		"""Prepare to log into IDS via dynamic code.

		:param account: Username (i.e. phone number) and \
		password (i.e. dynamic code).
		:return: Cookies and login state.
		"""
		ret = {"cookies": None, "logged_in": False}
		url = "https://ids.xidian.edu.cn/authserver/login"
		data = {
			"username": account["username"],
			"dynamicCode": account["password"], "captcha": "",
			"captcha": "", "_eventId": "submit",
			"cllt": self.__secrets["login_type"],
			"dllt": "generalLogin", "lt": "", "rememberMe": True,
			"execution": self.__secrets["login_execution"]
		}
		params = {"service": self.__service}
		res = await self.__session.post(
			url, data = data, params = params
		)
		if res.status == 200:
			ret.update({
				"cookies": self.__session.session_cookies,
				"logged_in": "CASTGC" in
				self.__session.session_cookies.filter_cookies(
					"https://ids.xidian.edu.cn/authserver"
				)
			})
		return ret

class Newesxidian:
	"""XDU exclusive APIs for classroom livestreams.
	"""
	__async_ctxmgr = __cx = None
	__logged_in = False

	def __init__(self, chaoxing: _Chaoxing = None):
		"""Create a Newesxidian with ``Chaoxing`` instance.

		:param chaoxing: The ``Chaoxing`` instance.
		"""
		if not self.__async_ctxmgr is None:
			return
		self.__cx = chaoxing

	async def __aenter__(self):
		if not self.__async_ctxmgr is None:
			return self
		self.__async_ctxmgr = True
		await self.__cx.__aenter__()
		if self.__cx.logged_in and self.__cx.fid == "16820":
			self.__logged_in = True
		return self

	async def __aexit__(self, *args, **kwargs):
		if not self.__async_ctxmgr:
			return
		self.__logged_in = False
		self.__async_ctxmgr = False

	@property
	def logged_in(self):
		return self.__logged_in

	async def livestream_get_url(self, livestream: dict = {"live_id": ""}):
		"""Get livestream URL.

		:param livesteam: Live ID in dictionary.
		:return: Livestream URL, live ID, device ID and \
		classroom location (``""``).
		URL will fallback to replay URL for non-ongoing live IDs.
		"""
		url = "https://newesxidian.chaoxing.com/live/getViewUrlHls"
		live_id = livestream["live_id"]
		params = {"liveId": live_id}
		res = await self.__cx.get(url, params = params, ttl = 86400)
		return {
			"url": await res.text(), "live_id": live_id,
			"device": "", "location": ""
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
		location = livestream.get("location") or ""
		device_code = livestream.get("device") or ""
		if not livestream.get("device"):
			url1 = "http://newesxidian.chaoxing.com/live/listSignleCourse"
			params1 = {"liveId": livestream.get("live_id") or ""}
			res1 = await self.__cx.get(
				url1, params = params1, ttl = 86400
			)
			for lesson in (await res1.json(
				content_type = None
			) or []):
				if f"{lesson['id']}" == livestream["live_id"]:
					device_code = lesson["deviceCode"]
					location = lesson["schoolRoomName"].rstrip()
					break
		url2 = "http://newesxidian.chaoxing.com/live/getViewUrlNoCourseLive"
		params2 = {"deviceCode": device_code, "status": 1}
		res2 = await self.__cx.get(url2, params = params2, ttl = 86400)
		return {
			"url": await res2.text(), "live_id": params1["liveId"],
			"device": device_code, "location": location
		}

	async def curriculum_get_curriculum(self, week: str = ""):
		"""Get curriculum with livestreams.

		:param week: Week number. Defaulted to the current week.
		:return: Chaoxing curriculum with livestreams for lessons.
		"""
		async def _get_livestream(lesson):
			class_id = f"{lesson['teachClazzId']}"
			location = lesson["place"]
			live_id = f"{lesson['id']}"
			lesson = {
				"class_id": class_id,
				"course_id": f"{lesson['courseId']}",
				"name": lesson["courseName"],
				"locations": [location],
				"invite_code": "",
				"teachers": self.__cx.courses.get(
					class_id, {}
				).get("teachers", []),
				"times": [{
					"day": f"{lesson['weekDay']}",
					"period_begin": f"{lesson['jie']}",
					"period_end": f"{lesson['jie']}"
				}]
			}
			if not class_id in curriculum["lessons"]:
				curriculum["lessons"][class_id] = lesson
			else:
				_ts = curriculum["lessons"][class_id]["times"]
				t = lesson["times"][0]
				for _t in _ts:
					b = int(t["period_begin"])
					e = int(t["period_end"])
					_b = int(_t["period_begin"])
					_e = int(_t["period_end"])
					if _b <= b and e <= _e:
						break
				else:
					_ts.append(t)
			ls = await self.livestream_get_live_url(livestream = {
				"live_id": live_id, "location": location
			})
			_ls = curriculum["lessons"][class_id].setdefault(
				"livestreams", []
			)
			for l in _ls:
				if l["device"] == ls["device"]:
					return
			_ls.append(ls)
		curriculum = await self.__cx.curriculum_get_curriculum(
			week = week
		)
		url = "https://newesxidian.chaoxing.com/frontLive/listStudentCourseLivePage"
		params = {
			"fid": 16820, "userId": self.__cx.uid,
			"termYear": curriculum["details"]["year"],
			"termId": curriculum["details"]["semester"],
			"week": week or curriculum["details"]["week"]
		}
		res = await self.__cx.get(url, params = params, ttl = 86400)
		data = await res.json(content_type = None) or []
		await _gather(*(_create_task(
			_get_livestream(lesson)
		) for lesson in data))
		return curriculum
