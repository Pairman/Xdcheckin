__all__ = ("video_get_img", "img_scan")

from io import BytesIO as _BytesIO
from shutil import which as _which
from subprocess import Popen as _Popen, PIPE as _PIPE
from aiohttp import request as _request

try:
	from PIL.Image import open as _open, Image as _Image
except ImportError:
	class _Image:
		"""Dummy fallback for ``PIL.Image.Image``.
		"""
		height = width = 0
		def __enter__(self):
			return self
		def __exit__(self, *args):
			pass
	def _open(fp, mode = None, formats = None):
		"""Dummy fallback for ``PIL.Image.open()``.
		"""
		return _Image()

try:
	from imageio_ffmpeg import get_ffmpeg_exe as _get_ffmpeg_exe
	_ffmpeg = _get_ffmpeg_exe()
except ImportError:
	_ffmpeg = "ffmpeg" if _which("ffmpeg") else None

if _ffmpeg:
	async def video_get_img(url: str, ses = None, len_limit: int = 256):
		"""Extract an frame from an M3U8 stream. \
		Needs ``xdcheckin[image]`` to be installed.

		:param url: URL of the stream.
		:param ses: An ``aiohttp.ClientSession`` instance. Optional.
  		:param len_limit: \
		Limit of length of the M3U8 data. Default is ``384``.
		:return: Frame in ``PIL.Image.Image`` on success.
		"""
		try:
			if ses:
				res = await ses.get(url, headers = {})
				assert (
					res.status == 200 and
					res.content_length < len_limit
				)
				text = await res.text()
			else:
				async with _request("GET", url) as res:
					assert (
						res.status == 200 and
						res.content_length < len_limit
					)
					text = await res.text()
			ts = text.split()[-1]
			assert ts.endswith(".ts")
			proc = _Popen((
				_ffmpeg, "-v", "quiet",
				"-i", f"{url[: url.rfind('/')]}/{ts}",
				"-vf", "select='eq(n\\,23)'", "-vframes", "1",
				"-f", "image2", "-"
			), stdout = _PIPE)
			return _open(_BytesIO(proc.communicate()[0]))
		except Exception:
			return _Image()
else:
	async def video_get_img(url: str, ses = None, len_limit: int = 384):
		"""Dummy fallback for ``video_get_img()``. \
		Please install ``xdcheckin[image]``.

		:param url: URL of the stream.
		:param ses: An ``aiohttp.ClientSession`` instance. Optional.
		:return: Dummy ``PIL.Image.Image``.
		"""
		return _Image()

try:
	from pyzbar.pyzbar import decode as _decode, ZBarSymbol as _ZBarSymbol
	def img_scan(img):
		"""Scan and decode qrcodes in an Image. \
		Needs ``xdcheckin[image]`` to be installed.

		:param img: ``PIL.Image.Image`` Image.
		:return: Decoded strings.
		"""
		assert img.height and img.width
		return [s.data.decode("utf-8") for s in _decode(
			img, (_ZBarSymbol.QRCODE, )
		)]
except ImportError:
	def img_scan(img):
		"""Dummy fallback for ``img_scan()``. \
		Please install ``xdcheckin[image]``.

		:param img: ``PIL.Image.Image`` Image.
		:return: ``[]``.
		"""
		return []
