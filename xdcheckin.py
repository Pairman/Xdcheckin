from json import load, dump
from os import path
from utils.chaoxing import *

# Load config.
with open(path.dirname(__file__) + "/config.json", "r", encoding = "utf-8") as config_file:
	config = load(config_file)

# Login.
if not chaoxing_login_check(config.get("cookie")):
	ret = chaoxing_login(config["username"], config["password"])
	config["cookie"], config["name"], config["fid"], config["uid"] = ret["cookie"], ret["name"], ret["fid"], ret["uid"]
	if not chaoxing_login_check(config["cookie"]):
		exit("[xdcheckin] (login) failed.")
	print("[xdcheckin] (login) success.")
print("[xdcheckin] (login) session retrieved.")

# Save config.
with open(path.dirname(__file__) + "/config.json", "w", encoding = "utf-8") as config_file:
	dump(config, config_file, indent = "\t", ensure_ascii = False)

from cv2 import VideoCapture, imshow, waitKey, destroyAllWindows, QRCodeDetector

# Checkin.
video = VideoCapture(0)
qcd = QRCodeDetector()
decoded_data_set_old = set()
while True:
	frame = video.read()[1]
	decoded_data_set = set(qcd.detectAndDecodeMulti(frame)[1])
	if len(decoded_data_set) and decoded_data_set != decoded_data_set_old and sum((chaoxing_checkin_url_checkurl(url) for url in decoded_data_set)):
			print(decoded_data_set_old := decoded_data_set)
			for url in decoded_data_set:
				print("[xdcheckin] (checkin) %s" % "checkin success" if chaoxing_checkin_url(url, config, locations["B"]) else "checkin failed")
	imshow("frame", frame)
	if waitKey(1) & 0xFF == ord("q"):
		break
video.release()
destroyAllWindows()
