from multiprocessing import Process
from waitress import serve
from backend.server import server

server_proc = Process(target = serve, kwargs = {"app": server, "host": "127.0.0.1", "port": 5001})
server_proc.start()

from toga import App as toga_App, Box as toga_Box, MainWindow as toga_MainWindow, WebView as toga_WebView, Label as toga_Label
from toga.platform import current_platform as toga_platform_current_platform
from toga.style import Pack as toga_style_Pack

class Xdcheckin(toga_App):
	def startup(self):
		def _exit_handler(self):
			server_proc.terminate()
			server_proc.join()
			return self._on_exit
		self.on_exit = _exit_handler

		self.main_window = toga_MainWindow(title = self.formal_name)
		if toga_platform_current_platform == "android":
			from java import jclass
			Intent, Uri = jclass("android.content.Intent"), jclass("android.net.Uri")
			self._impl.native.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("http://127.0.0.1:5001")))
			self.main_window.content = toga_Box(
				children = [
					toga_Label("This APP will launch\nyour browser automatically.\nIf not, visit \"http://127.0.0.1:5001\"\nin you browser manually.", style = toga_style_Pack(padding = 12, font_size = 16))
				]
			)
		elif toga_platform_current_platform == "linux":
			from os import system
			system("xdg-open \"http://127.0.0.1:5001\"")
			self.main_window.content = toga_Box(
				children = [
					toga_Label("This APP will launch\nyour browser automatically.\nIf not, visit \"http://127.0.0.1:5001\"\nin you browser manually.", style = toga_style_Pack(padding = 12, font_size = 16))
				]
			)
		else:
			self.main_window.content = toga_Box(
				children = [
					toga_WebView(url = "http://127.0.0.1:5001", style = toga_style_Pack(flex = 1))
				]
			)
		self.main_window.show()

def main():
	return Xdcheckin()
