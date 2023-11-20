from json import loads
from os import path
import requests
from urllib.parse import parse_qs, unquote, urlparse

# Disable request warnings.
requests.packages.urllib3.disable_warnings()

# Create global session.
session = requests.session()

locations = {
	"A": "",
	'B': "{\"result\":1,\"latitude\":34.132297,\"longitude\":108.838367,\"address\":\"中国陕西省西安市长安区兴隆街道内环北路西安电子科技大学(南校区)\"}",
	"C": "",
	"信远": "",
}

def chaoxing_login(username: str, password: str):
	"""Login to Chaoxing account.
	:param username: Username.
	:param password: Password.
	:return: Login cookie and UID.
	"""
	params = {
		"code": password,
		"cx_xxt_passport": "json",
		"loginType": "1",
		"roleSelect": "true",
		"uname": username
	}
	url = "https://passport2-api.chaoxing.com/v11/loginregister"
	res = session.get(url, params = params)
	data = requests.utils.dict_from_cookiejar(session.cookies).items()
	cookie = "".join((key + "=" + val + ";" for key, val in data))
	d = loads(res.text)
	if d["mes"] == "验证通过":
		url = "https://sso.chaoxing.com/apis/login/userLogin4Uname.do"
		res = session.get(url)
		d = loads(res.text)
		if d["result"] == 1:
			return {"cookie": cookie, "uid": str(d["msg"]["puid"])}
	return {"cookie": "", "uid": ""}

def chaoxing_headers_get(cookie: str):
	"""Get chaoxing request headers.
	:param cookie: Login cookie.
	:return: request headers.
	"""
	ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 com.ssreader.ChaoXingStudy/ChaoXingStudy_3_4.8_ios_phone_202012052220_56 (@Kalimdor)_12787186548451577248"
	headers = {
		"Accept-Encoding": "gzip",
	    	"Accept-Language": "zh-Hans-CN;q=1, zh-Hant-CN;q=0.9",
		"Cookie": cookie,
		"User-Agent": ua
	}
	return headers

def chaoxing_login_check(cookie: str):
	"""Check chaoxing account login state.
	:param cookie: Login cookie.
	:return: 1 if login state valid else 0.
	"""
	url = "https://sso.chaoxing.com/apis/login/userLogin4Uname.do"
	res = requests.get(url, headers = chaoxing_headers_get(cookie))
	d = loads(res.text)
	return d["result"] == 1

def chaoxing_checkin_url(checkin_url: str, name, cookie, uid, location):
	params_l = parse_qs(urlparse(unquote(checkin_url)).query)
	active_id, enc = params_l["activeId"][0], params_l["enc"][0]
	url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
	params = {
		'enc': enc,
		'name': name,
		'activeId': active_id,
		'uid': uid,
		'location': location,
		'latitude': '-1',
		'longitude': '-1',
		'fid': '16820',
		'appType': '15'
	}
	res = requests.get(url, params = params, headers = chaoxing_headers_get(cookie))
	return res.text == "success"