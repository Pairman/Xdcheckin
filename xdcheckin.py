from cv2 import VideoCapture, imshow, waitKey, destroyAllWindows, QRCodeDetector
from json import load
from chaoxing import *

def loc(username, password):
	"""Location checkin interface.
	Input activity IDs to checkin.
	"""
	cx = Chaoxing(username, password)
	if (not cx.logined):
		exit("[xdcheckin] (login) failed.")
	print("[xdcheckin] (login) successful.")
	while active_id := input():
		try:
			checkin = cx.checkin_checkin_location({"active_id": active_id}, locations["B"])
		except Exception:
			checkin = False
		print("[xdcheckin] (location_checkin) " + ("successful." if checkin else "failed."))

def qr(username, password):
	"""Qrcode checkin interface.
	Scan qrcodes to checkin.
	"""
	cx = Chaoxing(username, password)
	if (not cx.logined):
		exit("[xdcheckin] (login) failed.")
	print("[xdcheckin] (login) successful.")
	video = VideoCapture(0)
	qcd = QRCodeDetector()
	decoded_data_set_old = set()
	while True:
		frame = video.read()[1]
		decoded_data_set = set(qcd.detectAndDecodeMulti(frame)[1])
		if len(decoded_data_set) and tuple(decoded_data_set)[0] != "" and decoded_data_set != decoded_data_set_old:
				decoded_data_set_old = decoded_data_set
				for url in decoded_data_set:
					try:
						checkin = cx.checkin_checkin_qrcode_url(url, locations["B"])
					except Exception:
						checkin = False
					print("[xdcheckin] (qrcode_checkin) " + ("successful." if checkin else "failed."))
		imshow("frame", frame)
		if waitKey(1) & 0xFF == ord("q"):
			break
	video.release()
	destroyAllWindows()

if __name__ == "__main__":
	username = password = ""
	try:
		with open("config.json", "r", encoding = "utf-8") as config_file:
			config = load(config_file)
		assert (username := config["username"])
		assert (password := config["password"])
	except Exception:
		exit("[xdcheckin] (main) error loading config.")
	try:
		qr(username = username, password = password)
	except Exception:
		exit("[xdcheckin] (main) error checking in.")
