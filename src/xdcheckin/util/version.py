__all__ = ("compare_versions", "version")

from importlib.metadata import version as _version

def compare_versions(u: str, v: str):
	"""Compare two version strings in 'x.y.z' format.
	:param u: Version string.
	:param v: Another version string.
	:return: -1 if ``u`` < ``v`` or 1 if ``u`` > ``v``, otherwise 0.
	"""
	for m, n in zip(map(int, u.split(".")), map(int, v.split("."))):
		if m < n:
			return 1
		if m > n:
			return -1
	return 0

version = _version("xdcheckin")