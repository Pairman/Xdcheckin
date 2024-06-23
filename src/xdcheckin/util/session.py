__all__ = ("CachedSession", )

from asyncio import (
	create_task as _create_task, run as _run,
	get_event_loop as _get_event_loop
)
from atexit import register as _register
from signal import signal as _signal, SIGINT as _SIGINT, SIGTERM as _SIGTERM
try:
	from signal import SIGHUP as _SIGHUP
except Exception:
	_SIGHUP = None
from sys import exit as _exit
from aiocache import Cache as _Cache
from aiocache.serializers import NullSerializer as _NullSerializer
from aiohttp.client import (
	ClientSession as _ClientSession, ClientResponse as _ClientResponse
)
class _MockResponse:
	cookies, status = {}, 404

	async def json(self, *args, **kwargs):
		return {}

	async def read(self, *args, **kwargs):
		return b""

	async def text(self,  *args, **kwargs):
		return ""
	
class CachedSession:
	"""Wrapper for ``aiohttp.ClientSession`` with cache.
	"""
	__async_ctxmgr = headers = cookies = __session = __cache = None

	def __init__(
		self, headers: dict = None, cookies: dict = None,
		cache_enabled: bool = True
	):
		"""Create a ``CachedSession`` instance.
		:param headers: Default headers.
		:param cookies: Default cookies.
		:param cache_enabled: Whether to enable caching.
		"""
		if not self.__async_ctxmgr is None:
			return
		self.headers = headers or {}
		self.cookies = cookies or {}
		self.__session = _ClientSession()
		if cache_enabled:
			self.__cache = _Cache(
				_Cache.MEMORY, serializer = _NullSerializer()
			)
		def _release():
			try:
				_loop = _get_event_loop()
			except Exception:
				_loop = None
			_coro = self.__aexit__(None, None, None)
			if _loop and _loop.is_running():
				_loop.create_task(_coro)
			else:
				_run(_coro)
		def _sighandler(sig, frame):
			_release()
			_exit(0)
		_register(_release)
		if _SIGHUP:
			_signal(_SIGHUP, _sighandler)
		_signal(_SIGINT, _sighandler)
		_signal(_SIGTERM, _sighandler)

	async def __aenter__(self):
		if not self.__async_ctxmgr is None:
			return self
		self.__async_ctxmgr = True
		await self.__session.__aenter__()
		return self

	async def __aexit__(self, *args, **kwargs):
		if self.__async_ctxmgr != True:
			return
		await self.__session.__aexit__(*args, **kwargs)
		self.__async_ctxmgr = False

	@property
	def session_cookies(self):
		return self.__session.cookie_jar

	async def close(self):
		await self.__aexit__(None, None, None)

	async def __cache_handler(
		self, func, ttl: int, *args, **kwargs
	) -> _ClientResponse:
		if not self.__cache or not ttl:
			return await func(*args, **kwargs)
		key = f"{func.__name__}{args}{kwargs.items()}"
		try:
			res = await self.__cache.get(key)
		except Exception:
			res = _MockResponse()
		if not res:
			res = await func(*args, **kwargs)
			if res.status == 200 or res.status == 500:
				_create_task(self.__cache.set(key, res, ttl))
		return res

	async def get(
		self, url: str, params: dict = None, cookies: dict = None,
		headers: dict = None, ttl: int = 0, **kwargs
	) -> _ClientResponse:
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
	) -> _ClientResponse:
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
