from time import time as _time

class TimestampDict:
	"""Timestamped dictionary for easy vacuuming.
	"""
	__values = {}
	__timestamps = {}

	def __contains__(self, key):
		return key in self.__values

	def __getitem__(self, key):
		"""Return self[key].
		"""
		if key in self.__values:
			return self.__values[key]
		raise KeyError(key)

	def __setitem__(self, key, value):
		"""Set self[key] to value.
		"""
		self.__values[key] = value
		self.__timestamps[key] = _time()

	def __delitem__(self, key):
		"""Delete self[key].
		"""
		del self.__values[key], self.__timestamps[key]

	def __iter__(self):
		"""Implement iter(self).
		"""
		return iter(self.__values)

	def __len__(self):
		"""Return len(self).
		"""
		return len(self.__values)

	def keys(self):
		"""D.keys() -> a set-like object providing a view on D's keys.
		"""
		return self.__values.keys()

	def values(self):
		"""D.values() -> an object providing a view on D's values.
		"""
		return self.__values.values()

	def get(self, key, default = None):
		"""Return the value for key if key is in the dictionary, \
		else default.
		"""
		return self.__values.get(key, default)

	def vacuum(self, seconds):
		"""Delete self[key] for keys set older than \
		the specified seconds.
		"""
		now = _time()
		for key, timestamp in tuple(self.__timestamps.items()):
			if now > timestamp + seconds:
				del self[key]
