from time import localtime as _localtime, strftime as _strftime

strftime = lambda ts: _strftime("%Y-%m-%d %H:%M:%S", _localtime(ts))

r