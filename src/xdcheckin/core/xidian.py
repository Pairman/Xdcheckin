# -*- coding: utf-8 -*-

from asyncio import create_task as _create_task, gather as _gather
from re import search as _search
from time import time as _time
from xdcheckin.core.chaoxing import Chaoxing as _Chaoxing
from xdcheckin.util.encryption import encrypt_aes as _encrypt_aes
from xdcheckin.util.session import CachedSession as _CachedSession

class IDSSession:
	config = {
		"requests_headers": {
			"User-Agent":
				"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit"
				"/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 M"
				"obile Safari/537.36"
		}
	}
	__session = __secrets = __service = None
	logined = False

	def __init__(self, service: str = ""):
		"""Initialize an IDS Session.
		:param service: The SSO service for redirection.
		"""
		if self.logined:
			return
		self.__session = _CachedSession()
		self.__secrets, self.__service = {}, service

	async def __aenter__(self):
		await self.__session.__aenter__()
		return self

	async def __aexit__(self, *args, **kwargs):
		await self.__session.__aexit__(*args, **kwargs)

	async def get(self, *args, **kwargs):
		return await self.__session.get(*args, **kwargs)

	async def post(self, *args, **kwargs):
		return await self.__session.post(*args, **kwargs)

	async def login_username_prepare(self):
		"""Prepare verification for username login.
		:return: Base64 encoded captcha background and \
		slider image string.
		"""
		url1 = "https://ids.xidian.edu.cn/authserver/login"
		params1 = {"service": self.__service}
		res1 = await self.__session.get(url = url1, params = params1)
		ret = {"big_img_src": "", "small_img_src": ""}
		if not res1 or not res1.status == 200:
			return ret
		s = _search(
			r"\"pwdEncryptSalt\" value=\"(.*?)\".*?"
			r"\"execution\" value=\"(.*?)\"", await res1.text()
		)
		url2 = "https://ids.xidian.edu.cn/authserver/common/openSliderCaptcha.htl"
		params2 = {"_": str(int(1000 * _time()))}
		res2 = await self.__session.get(url = url2, params = params2)
		if not res2 or not res2.status == 200:
			return ret
		data = await res2.json()
		ret.update({
			"big_img_src": data["bigImage"],
			"small_img_src": data["smallImage"]
		})
		self.__secrets.update({
			"login_prepare_salt": s.group(1),
			"login_prepare_execution": s.group(2)
		})
		return ret

	async def login_username_finish(
		self,
		account: dict = {"username": "", "password": "", "vcode": ""}
	):
		"""Verify and finish username logging in.
		:param account: Username, password and verification \
		code (e.g. slider offset).
		:return: Cookies and login state.
		"""
		url1 = "https://ids.xidian.edu.cn/authserver/common/verifySliderCaptcha.htl"
		data1 = {"canvasLength": 280, "moveLength": account["vcode"]}
		res1 = await self.__session.post(url1, data = data1)
		ret = {"cookies": None, "logined": False}
		if not res1 or (not res1.status == 200 and \
		(await res1.json())["errorCode"] == 1):
			return ret
		password = _encrypt_aes(
			msg = account["password"],
			key = self.__secrets["login_prepare_salt"].encode("utf-8"),
			iv = b"xidianscriptsxdu",
			pad = lambda msg: 4 * b"xidianscriptsxdu" + msg.encode("utf-8")
		)
		url2 = "https://ids.xidian.edu.cn/authserver/login"
		data2 = {
			"username": account["username"], "password": password,
			"captcha": "", "_eventId": "submit",
			"cllt": "userNameLogin", "dllt": "generalLogin",
			"execution": self.__secrets["login_prepare_execution"],
			"lt": "", "rememberMe": True
		}
		params2 = {"service": self.__service}
		res2 = await self.__session.post(
			url2, data = data2, params = params2
		)
		if not res2 or not res2.status == 200:
			return ret
		ret.update({"cookies": self.__session.cookies, "logined": True})
		return ret

	async def login_cookies(self, account: dict = {"cookies": None}):
		"""Login with cookies.
		:param account: Cookies.
		:return: Cookies and login state.
		"""
		url = "http://ids.xidian.edu.cn/authserver/index.do"
		res = await self.__session.get(
			url = url, cookies = account["cookies"],
			allow_redirects = False
		)
		ret = {"cookies": None, "logined": False}
		if not res or res.status == 302:
			return ret
		ret.update({"cookies": account["cookies"], "logined": True})
		return ret

class Newesxidian:
	"""XDU exclusive APIs for classroom livestreams.
	"""
	__chaoxing = logined = None

	def __init__(self, chaoxing: _Chaoxing = None):
		"""Create a Newesxidian with ``Chaoxing`` instance.
		:param chaoxing: The ``Chaoxing`` instance.
		:return: None.
		"""
		if not chaoxing.logined or not chaoxing.fid == "16820":
			return
		self.logined, self.__chaoxing = True, chaoxing

	async def __aenter__(self):
		await self.__chaoxing.__aenter__()
		return self

	async def __aexit__(self, *args, **kwargs):
		await self.__chaoxing.__aexit__(*args, **kwargs)

	async def livestream_get_url(self, livestream: dict = {"live_id": ""}):
		"""Get livestream URL.
		:param livesteam: Live ID in dictionary.
		:return: Livestream URL, live ID, device ID and 
		classroom location (``""``).
		URL will fallback to replay URL for non-ongoing live IDs.
		"""
		url = "https://newesxidian.chaoxing.com/live/getViewUrlHls"
		params = {"liveId": livestream["live_id"]}
		res = await self.__chaoxing.get(
			url = url, params = params, ttl = 86400
		)
		return {
			"url": await res.text(),
			"live_id": livestream["live_id"],
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
		url1 = "http://newesxidian.chaoxing.com/live/listSignleCourse"
		params1 = {"liveId": livestream.get("live_id") or ""}
		url2 = "http://newesxidian.chaoxing.com/live/getViewUrlNoCourseLive"
		params2 = {
			"deviceCode": livestream.get("device") or "","status": 1
		}
		location = livestream.get("location") or ""
		if not livestream.get("device"):
			res1 = await self.__chaoxing.get(
				url = url1, params = params1, ttl = 86400
			)
			for lesson in (await res1.json() or []):
				if str(lesson["id"]) == livestream["live_id"]:
					params2["deviceCode"] = lesson["deviceCode"]
					location = lesson["schoolRoomName"].rstrip()
					break
		res2 = await self.__chaoxing.get(
			url = url2, params = params2, ttl = 86400
		)
		return {
			"url": await res2.text(), "live_id": params1["liveId"],
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
		curriculum = await self.__chaoxing.curriculum_get_curriculum(
			week = week
		)
		url = "https://newesxidian.chaoxing.com/frontLive/listStudentCourseLivePage"
		params = {
			"fid": 16820, "userId": self.__chaoxing.uid,
			"termYear": curriculum["details"]["year"],
			"termId": curriculum["details"]["semester"],
			"week": week or curriculum["details"]["week"]
		}
		res = await self.__chaoxing.get(
			url = url, params = params, ttl = 86400
		)
		data = (await res.json() or []) if res else []
		await _gather(*[
			_create_task(_get_livestream(lesson)) for lesson in data
		])
		return curriculum
