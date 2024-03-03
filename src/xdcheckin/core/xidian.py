# -*- coding: utf-8 -*-

from threading import Thread
from xdcheckin.core.chaoxing import Chaoxing

class Newesxidian:
	"""XDU exclusive APIs for classroom livestreams.
	"""
	chaoxing_session = logined = None

	def __init__(self, chaoxing: Chaoxing = None):
		if self.logined or not chaoxing.logined or not chaoxing.cookies.get("fid", 0) == "16820":
			return
		self.logined, self.chaoxing_session = True, chaoxing

	def livestream_get_url(self, livestream: dict = {"live_id": ""}):
		"""Get livestream URL.
		:param livesteam: Live ID in dictionary.
		:return: Livestream URL, live ID and device ID (placeholder). URL will fallback to replay URL for non-ongoing live IDs.
		"""
		url = "https://newesxidian.chaoxing.com/live/getViewUrlHls"
		params = {
			"liveId": livestream["live_id"]
		}
		res = self.chaoxing_session.get(url = url, params = params, expire = 86400)
		return {
			"url": res.text,
			"live_id": livestream["live_id"],
			"device": ""
		}

	def livestream_get_live_url(self, livestream: dict = {"live_id": "", "device": ""}):
		"""Get livestream URL.
		:param livestream: Live ID (unused if device ID is present) or device ID in dictionary.
		:return: Livestream URL, live ID (placeholder if not given) and device ID.
		"""
		url1 = "http://newesxidian.chaoxing.com/live/listSignleCourse"
		params1 = {
			"liveId": livestream.get("live_id", "")
		}
		url2 = "http://newesxidian.chaoxing.com/live/getViewUrlNoCourseLive"
		params2 = {
			"deviceCode": livestream.get("device", ""),
			"status": 1
		}
		if not livestream.get("device"):
			res1 = self.chaoxing_session.get(url = url1, params = params1, expire = 86400)
			data = res1.json() or []
			for lesson in data:
				if str(lesson["id"]) == livestream["live_id"]:
					params2["deviceCode"] = lesson["deviceCode"]
					break
		res2 = self.chaoxing_session.get(url = url2, params = params2, expire = 86400)
		return {
			"url": res2.text,
			"live_id": params1["liveId"],
			"device": params2["deviceCode"]
		}

	def curriculum_get_curriculum(self):
		"""Get curriculum with livestream URLs.
		:return: Chaoxing curriculum with livestream URL, live ID and CCTV device ID for lessons.
		"""
		def _get_livestream_wrapper(class_id: str = "", live_id: str = ""):
			curriculum["lessons"][class_id]["livestream"] = self.livestream_get_live_url(livestream = {"live_id": live_id})
		url = "https://newesxidian.chaoxing.com/frontLive/listStudentCourseLivePage"
		params = {
			"fid": 16820,
			"userId": self.chaoxing_session.cookies["UID"],
			"termYear": 0,
			"termId": 0,
			"week": 0
		}
		curriculum = self.chaoxing_session.curriculum_get_curriculum()
		params.update({
			"termYear": curriculum["details"]["year"],
			"termId": curriculum["details"]["semester"],
			"week": curriculum["details"]["week"]
		})
		res = self.chaoxing_session.get(url = url, params = params, expire = 86400)
		data = res.json() or []
		threads = tuple(Thread(target = _get_livestream_wrapper, kwargs = {"class_id": class_id, "live_id": live_id}) for class_id, live_id in {str(lesson["teachClazzId"]): str(lesson["id"]) for lesson in data}.items())
		tuple(thread.start() for thread in threads)
		tuple(thread.join() for thread in threads)
		return curriculum
