from json import loads
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

def chaoxing_login(username: str, password: str, verify: int = 0):
	"""Login to Chaoxing account.
	:param username: Username.
	:param password: Password.
	:param verify: SSL certificate verification toggle.
	:return: Cookie, name, FID and UID in dictionary.
	"""
	params = {
		"code": password,
		"cx_xxt_passport": "json",
		"loginType": "1",
		"roleSelect": "true",
		"uname": username
	}
	url = "https://passport2-api.chaoxing.com/v11/loginregister"
	res = session.get(url, params = params, verify = verify)
	data = requests.utils.dict_from_cookiejar(session.cookies).items()
	cookie = "".join((key + "=" + val + ";" for key, val in data))
	d = loads(res.text)
	if d["mes"] == "验证通过":
		url = "https://sso.chaoxing.com/apis/login/userLogin4Uname.do"
		res = session.get(url, verify = verify)
		d = loads(res.text)
		if d["result"] == 1:
			name, fid, uid = str(d["msg"]["name"]), str(d["msg"]["fid"]), str(d["msg"]["puid"])
			return {"cookie": cookie, "name": name, "fid": fid, "uid": uid}
	return {"cookie": "", "name": "", "fid": fid, "uid": ""}

def chaoxing_headers(cookie: str):
	"""Get chaoxing request headers.
	:param cookie: Cookie.
	:return: Headers.
	"""
	ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 com.ssreader.ChaoXingStudy/ChaoXingStudy_3_6.2.3_ios_phone_202311102230_219 (@Kalimdor)_9048867483954592879"
	headers = {
		"Accept-Encoding": "gzip",
	    	"Accept-Language": "en-US,en;q=0.9",
		"User-Agent": ua,
		"Cookie": cookie
	}
	return headers

def chaoxing_login_check(cookie: str, verify: int = 0):
	"""Check chaoxing account login state.
	:param cookie: Cookie.
	:param verify: SSL certificate verification toggle.
	:return: Returns 1 if login is valid, otherwise 0.
	"""
	url = "https://sso.chaoxing.com/apis/login/userLogin4Uname.do"
	res = requests.get(url, headers = chaoxing_headers(cookie), verify = verify)
	d = loads(res.text)
	return d["result"] == 1

def chaoxing_checkin_url_checkurl(checkin_url: str):
	"""Check if URL is valid qrcode-Location checkin URL.
	:return: Returns 1 if valid, otherwise 0.
	"""
	return not checkin_url.find("https://mobilelearn.chaoxing.com/widget/sign/e")

def chaoxing_checkin_url(checkin_url: str, userinfo: dict[str, str], location: str, verify: int = 0):
	"""Qrcode-location checkin.
	:param checkin_url: URL from checkin qrcode.
	:param userinfo: Cookie, name, FID and UID in dictionary.
	:param location: Location.
	:param verify: SSL certificate verification toggle.
	:return: Returns 1 if checkin success, otherwise 0.
	"""
	params_l = parse_qs(urlparse(unquote(checkin_url)).query)
	name, uid, fid, cookie = userinfo["name"], userinfo["uid"], userinfo["fid"], userinfo["cookie"]
	active_id, enc = params_l["id"][0], params_l["enc"][0]
	url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
	params = {
		'enc': enc,
		'name': name,
		'activeId': active_id,
		'uid': uid,
		'location': location,
		'latitude': '-1',
		'longitude': '-1',
		'fid': fid,
		'appType': '15'
	}
	res = requests.get(url, params = params, headers = chaoxing_headers(cookie), verify = verify)
	return res.text == "success"
