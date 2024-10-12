__all__ = ("video_get_img", "img_scan")

from asyncio.subprocess import (
	create_subprocess_exec as _create_subprocess_exec,
	PIPE as _PIPE
)
from io import BytesIO as _BytesIO
from aiohttp import request as _request

try:
	from xdcheckin_ffmpeg import ffmpeg as _get_ffmpeg
	_ffmpeg = _get_ffmpeg()
except ImportError:
	_ffmpeg = None

try:
	from PIL.Image import open as _open
	_is_has_pil = True
except ImportError:
	_is_has_pil = False

async def _video_m3u8_get_ts_url(url: str, ses = None, len_limit = 256):
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
	return ts

if _ffmpeg and _is_has_pil:
	async def video_get_img(url: str, ses = None, len_limit: int = 256):
		"""Extract an frame from a video stream. \
		Needs ``xdcheckin[image]`` to be installed.

		:param url: URL of the stream.
		:param ses: An ``aiohttp.ClientSession`` instance. Optional.
  		:param len_limit: \
		Limit of length of the M3U8 data. Default is ``256``.
		:return: Frame in ``PIL.Image.Image`` on success.
		"""
		url = url.strip()
		if url.startswith("rtsp://"):
			proc = await _create_subprocess_exec(
				_ffmpeg, "-rtsp_transport", "tcp",
				"-v", "quiet", "-i", url, "-an",
				"-vframes", "1", "-f", "image2", "-",
				stdout = _PIPE
			)
		else:
			if url.endswith(".m3u8"):
				ts = await _video_m3u8_get_ts_url(
					url = url, ses = ses,
					len_limit = len_limit
				)
				url = f"{url[: url.rfind('/')]}/{ts}"
			proc = await _create_subprocess_exec(
				_ffmpeg, "-v", "quiet", "-i", url, "-an",
				"-vframes", "1", "-f", "image2", "-",
				stdout = _PIPE
			)
		img = _open(_BytesIO((await proc.communicate())[0]))
		return img
else:
	class _Image:
		"""Dummy fallback for ``PIL.Image.Image``.
		"""
		info = {"msg": (
			"Please install ``xdcheckin[image]``. "
			f"FFmpeg: {not not _ffmpeg}, PIL: {_is_has_pil}"
		)}
		height = width = 0
		def __enter__(self):
			return self
		def __exit__(self, *args):
			pass
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
