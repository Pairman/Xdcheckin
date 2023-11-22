from cv2 import VideoCapture, imshow, waitKey, destroyAllWindows, QRCodeDetector
from json import load
from utils.chaoxing import *

def scan_checkin():
	"""QR-Location checkin via camera scan.
	"""
	video = VideoCapture(0)
	qcd = QRCodeDetector()
	decoded_data_set_old = set()
	while True:
		frame = video.read()[1]
		decoded_data_set = set(qcd.detectAndDecodeMulti(frame)[1])
		if len(decoded_data_set) and decoded_data_set != decoded_data_set_old:
				print(decoded_data_set_old := decoded_data_set)
				for url in decoded_data_set:
					success = 0
					try:
						success = chaoxing_checkin_qrloc_checkin_url(url, config, locations["B"])
					except Exception:
						print(Exception)
					print("[xdcheckin] (scan_checkin) %s" % "checkin success" if success else "checkin failed")
		imshow("frame", frame)
		if waitKey(1) & 0xFF == ord("q"):
			break
	video.release()
	destroyAllWindows()

def loc_checkin():
	"""Location checkin from user input.
	"""
	while active_id := input():
		try:
			success = chaoxing_checkin_loc_checkin(active_id = active_id, userinfo = userinfo, location = locations["B"])
		except Exception:
			print(Exception)
		print("[xdcheckin] (loc_checkin) %s" % "checkin success" if success else "checkin failed")

if __name__ == "__main__":
	# Login.
	with open("config.json", "r", encoding = "utf-8") as config_file:
		config = load(config_file)
		if not (userinfo := chaoxing_login(config["username"], config["password"])):
			exit("[xdcheckin] (login) failed.")
		print("[xdcheckin] (login) success.")
	# Checkin.
	loc_checkin()
