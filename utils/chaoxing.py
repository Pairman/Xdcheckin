from json import loads
import requests
from urllib.parse import parse_qs, unquote, urlparse

# Disable request warnings.
requests.packages.urllib3.disable_warnings()

# Create global session.
session = requests.session()

locations = {
	"A": "",
	"B": "{\"result\":1,\"latitude\":34.132297,\"longitude\":108.838367,\""\
	     "address\":\"中国陕西省西安市长安区兴隆街道内环北路西安电子科技大学(南"\
	     "校区)\"}",
	"C": "",
	"信远": "",
}

def chaoxing_headers() -> dict[str, str]:
	"""Get request headers.
	:return: Request headers.
	"""
	ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_2 like Mac OS X) AppleWe"\
	     "bKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 com.ssreader.Cha"\
	     "oXingStudy/ChaoXingStudy_3_6.2.3_ios_phone_202311102230_219 (@Ka"\
	     "limdor)_9048867483954592879"
	data = requests.utils.dict_from_cookiejar(session.cookies)
	cookie = "".join((key + "=" + val + ";" for key, val in data.items()))
	headers = {
		"Accept-Encoding": "gzip, deflate, br",
	    	"Accept-Language": "en-US,en;q=0.9",
		"Cookie": cookie, 
		"User-Agent": ua,
		"sec-ch-ua-mobile": "?1",
		"sec-ch-ua-platform": "iOS",
		"Sec-Fetch-Dest": "empty",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "same-origin",
		"X-Requested-With": "XMLHttpRequest"
	}
	return headers

def chaoxing_login(username: str, password: str) -> dict[str, str]:
	"""Login to Chaoxing account.
	:param username: Username.
	:param password: Password.
	:return: Name, FID, TID and UID on success, otherwise empty dict.
	"""
	url = "https://passport2-api.chaoxing.com/v11/loginregister"
	params = {
		"code": password,
		"cx_xxt_passport": "json",
		"loginType": "1",
		"roleSelect": "true",
		"uname": username
	}
	res = session.get(url, params = params, verify = 0)
	d = loads(res.text)
	if d["mes"] == "验证通过":
		url = "https://sso.chaoxing.com/apis/login/userLogin4Uname.do"
		res = session.get(url, verify = 0)
		d = loads(res.text)
		if d["result"] == 1:
			data = requests.utils.dict_from_cookiejar(session.
					     			  cookies)
			return {
				"name": str(d["msg"]["name"]),
				"fid": data["fid"],
				"tid": data["_tid"],
				"uid": data["_uid"]
			}
	return {}

def chaoxing_login_check() -> bool:
	"""Unused. Check login state.
	:return: Returns True on valid login, otherwise False.
	"""
	url = "https://sso.chaoxing.com/apis/login/userLogin4Uname.do"
	res = session.get(url, headers = chaoxing_headers(), verify = 0)
	d = loads(res.text)
	return d["result"] == 1

def chaoxing_checkin_details(active_id: str) -> dict[str, str]:
	"""Get checkin details via checkin activity ID.
	:param active_id: Activity ID.
	:param msg: MSG code.
	:return: Checkin details including class ID and MSG code.
	"""
	url = "https://mobilelearn.chaoxing.com/newsign/signDetail"
	params = {
		"activePrimaryId": active_id,
		"type": "1"
	}
	res = session.get(url, params = params, verify = 0)
	return loads(res.text)

def chaoxing_checkin_presign(active_id: str, userinfo: dict[str, str],
			     sign_details: dict[str, str] = {}) -> bool:
	"""Checkin pre-sign.
	:param active_id: Activity ID.
	:param userinfo: TID and UID. 
	:return: Returns True on success, otherwise False.
	"""
	if not sign_details:
		sign_details = chaoxing_checkin_details(active_id = active_id)
	url = "https://mobilelearn.chaoxing.com/newsign/preSign"
	params = {
		"courseId": "",
		"classId": sign_details["clazzId"],
		"activePrimaryId": active_id,
		"general": "1",
		"sys": "1",
		"ls": "1",
		"appType": "15",
		"tid": userinfo["tid"],
		"uid": userinfo["uid"],
		"ut": "s"
	}
	res = session.get(url, params = params, headers = chaoxing_headers(),
			  verify = 0)
	return res.status_code == 200

def chaoxing_checkin_analysis(active_id: str) -> bool:
	"""Checkin analysis.
	:param active_id: Activity ID. 
	:return: Returns True on success, otherwise False.
	"""
	url = "https://mobilelearn.chaoxing.com/pptSign/analysis"
	params = {
		"vs": "1",
		"DB_STRATEGY": "RANDOM",
		"aid": active_id
	}
	res = session.get(url, params = params, headers = chaoxing_headers(),
			  verify = 0)
	code = res.text.split("'")[5]
	url = "https://mobilelearn.chaoxing.com/pptSign/analysis2"
	params = {
		"DB_STRATEGY": "RANDOM",
		"code": code
	}
	res = session.get(url, params = params, headers = chaoxing_headers(),
		   	  verify = 0)
	return res.text == "success"

def chaoxing_checkin_qrloc_checkin(active_id: str, enc: str,
				   userinfo: dict[str, str],
				   location: str) -> bool:
	"""Qrcode-location checkin.
	:param active_id: Activity ID.
	:param enc: ENC code.
	:param userinfo: Name, FID and UID.
	:param location: Location.
	:return: Returns True on success, otherwise False.
	"""
	sign_details = chaoxing_checkin_details(active_id)
	if not chaoxing_checkin_presign(active_id = active_id,
				 	userinfo = userinfo,
					sign_details = sign_details):
		return False
	if not chaoxing_checkin_analysis(active_id = active_id):
		return False
	url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
	params = {
		"enc": enc,
		"name": userinfo["name"],
		"activeId": active_id,
		"uid": userinfo["uid"],
		"clientip": "",
		"location": location,
		"latitude": sign_details["latitude"],
		"longitude": sign_details["longitude"],
		"fid": userinfo["fid"],
		"appType": "15"
	}
	res = session.get(url, params = params, headers = chaoxing_headers(),
		   	  verify = 0)
	return res.text == "success"

def chaoxing_checkin_qrloc_checkin_url(checkin_url: str,
				       userinfo: dict[str, str],
				       location: str) -> bool:
	"""Qrcode-location checkin via URL.
	:param checkin_url: URL from checkin qrcode.
	:param userinfo: Name, FID and UID.
	:param location: Location.
	:return: Returns True on success, otherwise False.
	"""
	if checkin_url.find("https://mobilelearn.chaoxing.com/widget/sign/e"):
		return False
	params = parse_qs(urlparse(unquote(checkin_url)).query)
	return chaoxing_checkin_qrloc_checkin(active_id = params["id"][0],
					      enc = params["enc"][0],
					      userinfo = userinfo,
					      location = location)

def chaoxing_checkin_loc_checkin(active_id: str, userinfo: dict[str, str],
				 location: str) -> bool:
	"""Location checkin.
	:param active_id: Activity ID.
	:param userinfo: Name, FID and UID.
	:param location: Location.
	:return: Returns True on success, otherwise False.
	"""
	sign_details = chaoxing_checkin_details(active_id)
	if not chaoxing_checkin_presign(active_id = active_id,
				 	userinfo = userinfo,
					sign_details = sign_details):
		return False
	if not chaoxing_checkin_analysis(active_id = active_id):
		return False
	url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
	params = {
		"name": userinfo["name"],
		"address": loads(location)["address"],
		"activeId": active_id,
		"uid": userinfo["uid"],
		"clientip": "",
		"latitude": loads(location)["latitude"],
		"longitude": loads(location)["longitude"],
		"fid": userinfo["fid"],
		"appType": "15",
		"ifTiJiao": str(int(sign_details["latitude"] ==
		      		    sign_details["longitude"] == 0)),
		"validate": ""
	}
	res = session.get(url, params = params, headers = chaoxing_headers(),
		   	  verify = 0)
	return res.text == "success"
