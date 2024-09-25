__all__ = ("video_get_img", "img_scan")

from io import BytesIO as _BytesIO
from subprocess import run as _run, Popen as _Popen, PIPE as _PIPE
from aiohttp import request as _request
from PIL.Image import open as _open, Image as _Image

try:
	from imageio_ffmpeg import get_ffmpeg_exe
	_ffmpeg = get_ffmpeg_exe()
except ImportError:
	_ffmpeg = None if _run(
		("ffmpeg", "-version"), stdout = _PIPE, stderr = _PIPE
	).returncode else "ffmpeg"

if _ffmpeg:
	async def video_get_img(url: str, ses = None):
		"""Extract an frame from an M3U8 stream. \
		Needs ``xdcheckin[image]`` to be installed.

		:param url: URL of the stream.
		:param ses: An ``aiohttp.ClientSession`` instance. Optional.
		:return: Frame in ``PIL.Image.Image`` on success.
		"""
		try:
			if ses:
				res = await ses.get(url)
				assert res.status == 200
				text = await res.text()
			else:
				async with _request("GET", url) as res:
					assert res.status == 200
					text = await res.text()
			ts = text.split("\r\n")[-2]
			assert ts.endswith(".ts")
			proc = _Popen((
				_ffmpeg, "-v", "quiet",
				"-i", f"{url[: url.rfind('/')]}/{ts}",
				"-vf", "select='eq(n\\,23)'", "-vframes", "1",
				"-f", "image2", "-"
			), stdout = _PIPE)
			ret = _open(_BytesIO(proc.communicate()[0]))
		except Exception:
			ret = _Image()
		finally:
			return ret
else:
	async def video_get_img(url: str, ses = None):
		"""Dummy fallback for ``video_get_img``. \
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
		"""Dummy fallback for ``img_scan``. \
		Please install ``xdcheckin[image]``.

		:param img: ``PIL.Image.Image`` Image.
		:return: ``[]``.
		"""
		return []
