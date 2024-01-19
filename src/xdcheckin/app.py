from threading import Thread
from toga import App as toga_App, Box as toga_Box, MainWindow as toga_MainWindow, WebView as toga_WebView
from toga.platform import current_platform as toga_platform_current_platform
from toga.style import Pack as toga_style_Pack
from waitress import serve
from backend.server import server

class Xdcheckin(toga_App):
	def startup(self):
		server.config["XDCHECKIN_VERSION"] = self.version
		Thread(target = serve, kwargs = {"app": server, "host": "127.0.0.1", "port": 5001}).start()
		self.main_window = toga_MainWindow(title = self.formal_name)
		self.main_window.content = toga_Box(
			children = [
				toga_WebView(url = "about:blank" if toga_platform_current_platform == "android" else "http://127.0.0.1:5001", style = toga_style_Pack(flex = 1))
			]
		)
		self.main_window.show()
		if toga_platform_current_platform == "android":
			from java import jclass
			Intent, Uri = jclass('android.content.Intent'), jclass('android.net.Uri')
			self._impl.native.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("http://127.0.0.1:5001")))

def main():
	return Xdcheckin()
