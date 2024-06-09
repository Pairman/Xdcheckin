__all__ = ()

from multiprocessing import Process as _Process
from toga import App as _App, Box as _Box, MainWindow as _MainWindow, \
WebView as _WebView, Label as _Label
from toga.platform import current_platform as _current_platform
from toga.style import Pack as _Pack
from xdcheckin.server.server import start_server as _start_server

_url = "http://127.0.0.1:5001"
_msg = f"This APP will launch\n your browser automatically.\n\
If not, visit \"{_url}\"\n in you browser manually."

class _Xdcheckin(_App):
	def startup(self):
		_Process(target = _start_server, daemon = True).start()
		self.main_window = _MainWindow(title = self.formal_name)
		if _current_platform == "android":
			from android.content import Intent
			from android.net import Uri
			self._impl.native.startActivity(
				Intent(Intent.ACTION_VIEW, Uri.parse(_url))
			)
			self.main_window.content = _Box(children = (_Label(
				_msg,
				style = _Pack(padding = 12, font_size = 16)
			), ))
		elif _current_platform == "linux":
			from os import system
			system(f"xdg-open \"{_url}\"")
			self.main_window.content = _Box(children = (_Label(
				_msg,
				style = _Pack(padding = 12, font_size = 16)
			), ))
		else:
			self.main_window.content = _Box(children = (_WebView(
				url = _url, style = _Pack(flex = 1)
			), ))
		self.main_window.show()
