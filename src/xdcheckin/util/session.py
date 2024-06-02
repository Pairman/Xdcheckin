from asyncio import create_task as _create_task
from aiocache import Cache as _Cache
from aiocache.serializers import NullSerializer as _NullSerializer
from aiohttp import ClientSession as _ClientSession

class CachedSession:
	"""Wrapper for ``aiohttp.ClientSession`` with cache.
	"""
	headers = cookies = verify = __session = __cache = None

	def __init__(
		self, headers: dict = None, cookies: dict = None,
		verify: bool = False, cache_enabled: bool = True
	):
		"""Create a ``CachedSession`` instance.
		:param headers: Default headers.
		:param cookies: Default cookies.
		:param verify: SSL verification.
		:param cache_enabled: Whether to enable caching.
		"""
		self.headers = headers or {}
		self.cookies = cookies or {}
		self.__session = _ClientSession()
		if cache_enabled:
			self.__cache = _Cache(
				_Cache.MEMORY, serializer = _NullSerializer()
			)

	async def __aenter__(self):
		await self.__session.__aenter__()
		return self

	async def __aexit__(self, *args, **kwargs):
		await self.__session.__aexit__(*args, **kwargs)

	async def close(self):
		await self.__aexit__()

	async def __cache_handler(self, func, ttl: int, *args, **kwargs):
		if not self.__cache or not ttl:
			return await func(*args, **kwargs)
		key = f"{func.__name__}{args}{sorted(kwargs.items())}"
		try:
			res = await self.__cache.get(key)
		except Exception:
			res = None
		if not res is None:
			return res
		try:
			res = await func(*args, **kwargs)
			assert res.status in (200, 500)
		except Exception:
			res = None
		else:
			_create_task(self.__cache.set(key, res, ttl = ttl))
		return res

	async def get(
		self, url: str, params: dict = None, cookies: dict = None,
		headers: dict = None, ttl: int = 0, **kwargs
	):
		"""Get request.
		:param url: URL.
		:param params: params.
		:param cookies: Cookies. Overrides existing cookies.
		:param headers: Headers. Overrides existing headers.
		:param ttl: Cache TTL in seconds. Disabled with 0 by default.
		:param **kwargs: Optional arguments for \
		``aiohttp.ClientSession().get()``.
		:return: Response on success.
		"""
		res = await self.__cache_handler(
			self.__session.get, ttl, url = url, params = params,
			headers = headers if headers else self.headers,
			cookies = cookies if cookies else self.cookies,
			**kwargs
		)
		return res

	async def post(
		self, url: str, data: dict = None, cookies: dict = None,
		headers: dict = None, ttl: int = 0, **kwargs
	):
		"""Post request.
		:param url: URL.
		:param data: data.
		:param cookies: Cookies. Overrides existing cookies.
		:param headers: Headers. Overrides existing headers.
		:param ttl: Cache TTL in seconds. Disabled with 0 by default.
		:param **kwargs: Optional arguments for \
		``aiohttp.ClientSession().get()``.
		:return: Response on success.
		"""
		res = await self.__cache_handler(
			self.__session.post, ttl, url = url, data = data,
			headers = headers if headers else self.headers,
			cookies = cookies if cookies else self.cookies,
			**kwargs
		)
		return res