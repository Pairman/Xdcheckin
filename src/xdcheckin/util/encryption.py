# -*- coding: utf-8 -*-

from base64 import b64encode as _b64encode
from Crypto.Cipher.AES import new as _new, block_size as _block_size, MODE_CBC as _MODE_CBC
from Crypto.Util.Padding import pad as _pad

def encrypt_aes(
	msg: str = "", key: bytes = b"", iv: bytes = b"",
	padding: None = lambda msg: msg.encode("utf-8")
):
	enc = _new(key, _MODE_CBC, iv).encrypt(_pad(
		padding, _block_size
	))
	return _b64encode(enc).decode("utf-8")
