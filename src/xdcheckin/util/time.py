__all__ = ("strftime", )

from time import localtime as _localtime, strftime as _strftime

def strftime(seconds: float):
	"""Format timestamp to localtime string.
	:param seconds: Timestamp in seconds.
	:return: Time in string.
	"""
	return _strftime("%Y-%m-%d %H:%M:%S", _localtime(seconds))