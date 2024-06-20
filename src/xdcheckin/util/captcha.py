__all__ = ("chaoxing_captcha_get_checksum", "solve_captcha")

from hashlib import md5 as _md5
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
	return key, token

def solve_captcha(big_img: None = None, small_img: None = None, border: int = 8):
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
	template = small_img.im.crop((
		x_l, y_t, x_r, y_b
	)).convert("L", 3)
	mean_t = sum(template) / len(template)
	template = [v - mean_t for v in template]
	ncc_max = x_max = 0
	width_w = x_r - x_l
	height_w = y_b - y_t
	len_w = width_w * height_w
	width_g = big_img.width - small_img.width + width_w - 1
	grayscale = big_img.im.crop((
		x_l + 1, y_t, x_l + width_g, y_b
	)).convert("L", 3)
	for x in range(0, width_g - width_w, 2):
		window = grayscale.crop((x, 0, x + width_w, height_w))
		mean_w = sum(window) / len_w
		sum_wt = 0
		sum_ww = 0
		for w, t in zip(window, template):
			w -= mean_w
			sum_wt += w * t
			sum_ww += w * w
		ncc = sum_wt / sum_ww
		if ncc > ncc_max:
			ncc_max = ncc
			x_max = x
	return x_max
