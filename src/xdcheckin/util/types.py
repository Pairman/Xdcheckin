__all__ = ("TimestampDict", )

from time import time as _time

class TimestampDict:
	"""Timestamped dictionary for easy vacuuming.
	"""
	_data = {}
	_ts = {}

	def __getitem__(self, key):
		"""Return ``self[key]``.
		"""
		if key in self._data:
			self._ts[key] = _time()
			return self._data[key]
		raise KeyError(key)

	def __setitem__(self, key, value):
		"""Set ``self[key]`` to value.
		"""
		self._ts[key] = _time()
		self._data[key] = value

	def __delitem__(self, key):
		"""Delete ``self[key]``.
		"""
		del self._ts[key], self._data[key]

	def get(self, key, default = None):
		"""Return the value for key if key is in the dictionary, \
  		else default.
		"""
		if key in self._data:
			return self[key]
		return default

	def setdefault(self, key, default = None):
		"""Return the value for key if key is in the dictionary, \
  		else set the value to default and return default.
		"""
		if key in self._data:
			return self[key]
		self[key] = default
		return default

	async def vacuum(self, seconds = 0, handler = None):
		"""Remove key and value pairs older than the given seconds. \
  		Calls ``handler`` on each of the values if given.
		"""
		now = _time()
		for k, t in tuple(self._ts.items()):
			if now > t + seconds:
				if handler:
					await handler(self[k])
				del self[k]
