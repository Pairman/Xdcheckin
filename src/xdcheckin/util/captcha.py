__all__ = ("chaoxing_captcha_get_checksum", "solve_captcha")

from hashlib import md5 as _md5
from math import trunc as _trunc
from time import time as _time
from uuid import uuid4 as _uuid4

def chaoxing_captcha_get_checksum(
	captcha: dict = {"captcha_id": "", "server_time": "", "type": ""}
):
	"""Generate key and token for CAPTCHA images.

 	:param: CAPTCHA ID, server timestamp and CAPTCHA type.
  	:return: CAPTCHA key and token.
 	"""
	id = captcha["captcha_id"]
	time = captcha["server_time"]
	type = captcha["type"]
	key = _md5(f"{time}{_uuid4()}".encode("utf-8")).hexdigest()
	token = f"""{_md5(
		f"{time}{id}{type}{key}".encode("utf-8")
	).hexdigest()}:{int(time) + 300000}"""
	iv = _md5(
		f"{id}{type}{_trunc(_time() * 1000)}{_uuid4()}".encode("utf-8")
	).hexdigest()
	return key, token, iv

def solve_captcha(big_img = None, small_img = None, border: int = 8):
	"""Slider CAPTCHA solver based on normalized cross-correlation.

	:param big_img: Background image with slider piece embedded.
	:param small_img: Slider image vertically aligned \
	with transparent padding.
	:param border: Border width of the slider piece. \
	8 by default for Chaoxing's and 24 recommended for IDS's.
	:return: Slider offset.
	"""
	big_img.load()
	small_img.load()
	x_l, y_t, x_r, y_b = small_img.im.getband(3).point((
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1
	), None).getbbox()
	x_l += border
	y_t += border
	x_r -= border
	y_b -= border
	template = small_img.im.crop((x_l, y_t, x_r, y_b)).convert("L", 3)
	width_w = x_r - x_l
	len_w = width_w * (y_b - y_t)
	mean_t = sum(template) / len_w
	template = [v - mean_t for v in template]
	width_g = big_img.width - small_img.width + width_w - 1
	grayscale = big_img.im.convert("L", 3)
	cols_w = [
		sum(grayscale[y * big_img.width + x] for y in range(y_t, y_b))
		for x in range(x_l + 1, width_g + 1)
	]
	cols_w_l = iter(cols_w)
	cols_w_r = iter(cols_w)
	sum_w = sum(next(cols_w_r) for _ in range(width_w))
	ncc_max = x_max = 0
	for x in range(x_l + 1, width_g - width_w, 2):
		sum_w = (
			sum_w - next(cols_w_l) - next(cols_w_l) +
			next(cols_w_r) + next(cols_w_r)
		)
		mean_w = sum_w / len_w
		ncc = 0
		sum_ww = 0.000001
		for w, t in zip(grayscale.crop((
			x, y_t, x + width_w, y_b
		)), template):
			w -= mean_w
			ncc += w * t
			sum_ww += w * w
		ncc /= sum_ww
		if ncc > ncc_max:
			ncc_max = ncc
			x_max = x
	return x_max - x_l - 1
