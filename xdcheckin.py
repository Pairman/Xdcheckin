from json import load, dump
from os import path
from utils.chaoxing import *

# Load config.
with open(path.dirname(__file__) + "/config.json", "r", encoding = "utf-8") as config_file:
	config = load(config_file)

# Login.
if not chaoxing_login_check(config["cookie"]):
	ret = chaoxing_login(config["username"], config["password"])
	config["cookie"], config["uid"] = ret["cookie"], ret["uid"]
	if not chaoxing_login_check(config["cookie"]):
		exit("[xdcheckin] (login) failed.")
	print("[xdcheckin] (login) success.")
print("[xdcheckin] (login) session retrieved.")

# Save config.
with open(path.dirname(__file__) + "/config.json", "w", encoding = "utf-8") as config_file:
	dump(config, config_file, indent = "\t", ensure_ascii = False)

# Checkin.
while checkin_url := input("[xdcheckin] (checkin) input checkin url: "):
	chaoxing_checkin_url(checkin_url, config["name"], config["cookie"], config["uid"], config["location"])
