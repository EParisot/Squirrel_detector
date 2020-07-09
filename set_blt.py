import os

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('blt_install.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


conf_files = {"bluez_conf_file" : "/etc/systemd/system/dbus-org.bluez.service",
				"blt_conf_file" : "/etc/bluetooth/main.conf",
				"blt_name_file" : "/etc/machine-info"}

def edit_blt_conf(f_name, f_path):
	with open(f_path, "rw") as f:
		f_content = f.read()
		f_content_split = f_content.split("[General]\n")
		if len(f_content_split) == 2:
			if f_content_split[1].startswith("DisablePlugins = pnat") or f_content_split[1].startswith("\n# SQRT AUTO CONFIG:"):
				logger.info("%s already configured" % f_name)
				return
			else:
				f.seek(0)
				#f.write("[General]\n\n# SQRT AUTO CONFIG:\nDisablePlugins = pnat\n" + f_content_split[1])
				logger.info("%s config Done." % f_name)

def edit_bluez_conf(f_name, f_path):
	with open(f_path, "rw") as f:
		f_content = f.read()
		f_content_split = f_content.split("ExecStart=/usr/lib/bluetooth/bluetoothd")
		if len(f_content_split) == 2:
			if f_content_split[1].startswith(" -C\nExecStartPost=/usr/bin/sdptool add SP\n") or f_content_split[0].endswith("\n# SQRT AUTO CONFIG:\n"):
				logger.info("%s already configured" % f_name)
				return
			else:
				f.seek(0)
				#f.write(f_content_split[0] + "\n# SQRT AUTO CONFIG:\nExecStart=/usr/lib/bluetooth/bluetoothd -C\nExecStartPost=/usr/bin/sdptool add SP\n" + f_content_split[1])
				logger.info("%s config Done." % f_name)

if __name__ == "__main__":
	for f_name, f_path in conf_files.items():
		if os.path.exists(f_path):
			if f_name == "blt_name_file":
				with open(f_path, "w+") as f:
					pass#f.write("PRETTY_HOSTNAME=SQuareRooT_Camera")
			elif f_name == "blt_conf_file":
				edit_blt_conf(f_name, f_path)
			elif f_name == "bluez_conf_file":
				edit_bluez_conf(f_name, f_path)
		elif f_name == "blt_name_file":
			with open(f_path, "w+") as f:
				pass#f.write("PRETTY_HOSTNAME=SQuareRooT_Camera")
		else:
			logger.info("Bluetooth files not installed, please run './install.sh' first.")
			exit(0)

	
