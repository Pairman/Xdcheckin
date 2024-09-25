__all__ = ("classroom_urls", "classroom_url_get_single")

from ast import literal_eval as _literal_eval
from os.path import join as _join
from pkgutil import get_data as _get_data
from urllib.parse import parse_qs as _parse_qs, urlparse as _urlparse

_classroom_urls_str = _get_data(
	"xdcheckin.server", _join("static", "g_classroom_urls.js")
).decode("utf-8")

classroom_urls = {}
for val in _literal_eval(_classroom_urls_str[
	_classroom_urls_str.index("{") : _classroom_urls_str.rindex("}") + 1
]).values():
	classroom_urls.update(val)

def classroom_url_get_single(url: str, key: str = "pptVideo"):
	"""Get URL of a single view from a combined classroom URL.

	:param url: Classroom URL.
	:param key: Keyword of the perspective. Default is ``'pptVideo'``.
	:return: Its URL.
	"""
	return _literal_eval(
		_parse_qs(_urlparse(url).query)["info"][0]
	)["videoPath"].get(key, "") if url else ""
