__all__ = ("encrypt_aes", "chaoxing_get_identifier", "chaoxing_get_devicecode")

from base64 import b64encode as _b64encode
from hashlib import md5 as _md5
from uuid import getnode as _getnode
from Crypto.Cipher.AES import (
	new as _new, block_size as _block_size, MODE_CBC as _MODE_CBC,
	MODE_ECB as _MODE_ECB
)
from Crypto.Util.Padding import pad as _pad

def encrypt_aes(
	msg: str = "", key: bytes = b"", iv: bytes = b"",
	mode: int = _MODE_CBC, pad = lambda msg: msg.encode("utf-8")
):
	"""AES encryption.
	:param msg: Data in string.
	:param key: Key in bytes.
	:param iv: Initialization vector in bytes.
	:param pad: Padder for the data. PKCS7 by default.
	:return: Encrypted data in base64 string.
	"""
	return _b64encode((
		_new(key, mode) if mode == _MODE_ECB else _new(key, mode, iv)
	).encrypt(_pad(pad(msg), _block_size))).decode("utf-8")

def chaoxing_get_identifier(seed: str = ""):
	"""Get the 'Kalimdor' device identifier in Chaoxing's UA.
	:param seed: Seed.
	:return: Device identifier.
	"""
	return _md5(f"{_getnode()}{seed}".encode("utf-8")).hexdigest()

def chaoxing_get_devicecode(ident: str = ""):
	"""Get device code for Chaoxing's checking-in.
	:param ident: Device identifier.
	:return: Device code.
	"""
	return encrypt_aes(
		msg = ident, key = b"QrCbNY@MuK1X8HGw", iv = None,
		mode = _MODE_ECB
	)