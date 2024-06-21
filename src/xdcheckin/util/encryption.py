__all__ = ("encrypt_aes", )

from base64 import b64encode as _b64encode
from Crypto.Cipher.AES import (
	new as _new, block_size as _block_size, MODE_CBC as _MODE_CBC
)
from Crypto.Util.Padding import pad as _pad

def encrypt_aes(
	msg: str = "", key: bytes = b"", iv: bytes = b"",
	pad: None = lambda msg: msg.encode("utf-8")
):
	"""AES encryption.
	:param msg: Data in string.
	:param key: Key in bytes.
	:param iv: Initialization vector in bytes.
	:param pad: Padder for the data. PKCS7 by default.
	:return: Encrypted data in base64 string.
	"""
	return _b64encode(_new(key, _MODE_CBC, iv).encrypt(
		_pad(pad(msg), _block_size)
	)).decode("utf-8")
