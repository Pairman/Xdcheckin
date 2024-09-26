__all__ = ("is_valid_ip", "is_valid_host", "is_has_ipv6")

from errno import EADDRNOTAVAIL as _EADDRNOTAVAIL, EAFNOSUPPORT as _EAFNOSUPPORT
from socket import (
	has_ipv6 as _has_ipv6, getaddrinfo as _getaddrinfo,
	inet_pton as _inet_pton, socket as _socket, SOCK_STREAM as _SOCK_STREAM,
	AF_INET as _AF_INET, AF_INET6 as _AF_INET6, gaierror as _gaierror
)

def is_valid_ip(ip: str):
	"""Check if an IP address is valid.

	:param ip: IP address.
	:return: ``4`` for IPv4 and ``6`` for IPv6 if valid.
	"""
	try:
		_inet_pton(_AF_INET, ip)
		return 4
	except OSError:
		pass
	try:
		_inet_pton(_AF_INET6, ip)
		return 6
	except OSError:
		pass
	return 0

def is_valid_host(host: str):
	"""Check if a host is valid.

	:param host: Hostname, domain name or IP address.
	:return: ``4`` for IPv4 address, ``6`` for IPv6 address, \
	``5`` for IPv4-resolvable host or domain name, or \
	``7`` for IPv6-resolvable host or domain name if valid.
	"""
	is_ip = is_valid_ip(host)
	if is_ip:
		return is_ip
	try:
		_getaddrinfo(host, None, _AF_INET)
		return 5
	except _gaierror:
		pass
	try:
		_getaddrinfo(host, None, _AF_INET6)
		return 7
	except _gaierror:
		pass
	return 0

def is_has_ipv6(error = True):
	"""Check if IPv6 is supported on the system.

	:return: True if supported.
	"""
	if not _has_ipv6:
		return False
	try:
		with _socket(_AF_INET6, _SOCK_STREAM) as sock:
			sock.bind(("::1", 0))
		return True
	except OSError as e:
		if (
			error and e.errno != _EAFNOSUPPORT and
			e.errno != _EADDRNOTAVAIL
		):
			raise
		return False
