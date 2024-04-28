from time import time as _time

class TimestampDict:
	"""Timestamped dictionary for easy vacuuming.
	"""
	_data = {}
	_ts = {}

	def __repr__(self):
		return repr(self._data)

	def __getitem__(self, key: None):
		"""Return self[key].
		"""
		if key in self._data:
			self._ts[key] = _time()
			return self._data[key]
		raise KeyError(key)

	def __setitem__(self, key: None, value: None):
		"""Set self[key] to value.
		"""
		self._ts[key] = _time()
		self._data[key] = value

	def __delitem__(self, key):
		"""Delete self[key].
		"""
		del self._ts[key]
		del self._data[key]

	def get(self, key: None, default: None = None):
		"""Return the value for key if key is in the dictionary, else default.
		"""
		return self._data.get(key, default)

	def vacuum(self, seconds):
		"""Remove key and value pairs older than the specified seconds.
		"""
		now = _time()
		for k, t in tuple(self._ts.items()):
			if now > t + seconds:
				del self[k]
