import os
import shutil
from unittest.mock import patch
import time
import subprocess
from bluetooth import *

SRC_FOLDER = "../out"
DST_FOLDER = "tmp"
BLT_NAME_FILE = "/etc/machine-info"

DEBUG = True

if DEBUG:
	import logging
	from logging.handlers import RotatingFileHandler

	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
	file_handler = RotatingFileHandler('blt_activity.log', 'a', 1000000, 1)
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(logging.DEBUG)
	logger.addHandler(stream_handler)

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
advertise_service( server_sock, "SQRT",
					service_id = uuid,
					service_classes = [ uuid, SERIAL_PORT_CLASS ],
					profiles = [ SERIAL_PORT_PROFILE ], 
					protocols = [ OBEX_UUID ] 
)

def build_command(addr, chan, src):
	return "obexftp --nopath --noconn --uuid none --bluetooth %s --channel %s -p %s" % (addr, chan, src)

""" The script manipulates the make_archive() implementation for 
	zip files by temporarily replacing os.path.isfile() with a 
	custom accept() function. """
_os_path_isfile = os.path.isfile
def accept(path):
    if path in [".gitkeep"]:
        return False
    return _os_path_isfile(path)

def run_server()
	try:
		while True:
			if DEBUG:
				logger.info("Waiting for connection on RFCOMM channel %d" % port)

			client_sock, client_info = server_sock.accept()
			if DEBUG:
				logger.info("Accepted connection from %s" % client_info)

			# scan for OBEX service
			services = find_service(name=None, uuid=None, address=client_info[0])
			OBEX_CHAN = None
			for service in services:
				if service["name"] == "OBEX Object Push":
					OBEX_CHAN = service["port"]
			if OBEX_CHAN == None:
				data = "Error OBEX service not found. exit"
				client_sock.send(data)
				continue

			try:
				data = client_sock.recv(1024)
				if len(data) == 0:
					continue
				if DEBUG:
					logger.info("received [%s]" % data)
				# Handle send request
				if data.decode() == "send":
					# Zip folder
					with patch("os.path.isfile", side_effect=accept):
						zipFile = shutil.make_archive(os.path.join(DST_FOLDER, "SQRT_" + time.strftime("%Y%m%d_%H%M%S")), 'zip', SRC_FOLDER)
					if DEBUG:
						logger.info("calling %s" % build_command(client_info[0], 
											OBEX_CHAN, 
											os.path.join(DST_FOLDER, zipFile)))
					res = subprocess.call(build_command(client_info[0], 
											OBEX_CHAN, 
											os.path.join(DST_FOLDER, zipFile)).split(" "))
					if DEBUG:
						logger.info("Sent archive with return code %s" % res)
					# Clean tmp folder
					os.remove(os.path.join(DST_FOLDER, zipFile))
					# End connexion
					if res == 255:
						data = 'Sent: ' + os.path.basename(zipFile) + " done."
					else:
						data = "Error sending archive."
					client_sock.send(data)
					raise KeyboardInterrupt
				
				# Handle name change request
				elif "name" in data.decode():
					new_name = data.decode().split("name ")[-1]
					if DEBUG:
						logger.info("change name to %s" % new_name)
					# edit BLT_NAME_FILE
					with open(BLT_NAME_FILE, "w") as f:
						f.write("PRETTY_HOSTNAME=" + new_name)
					subprocess.call(("service", "bluetooth", "restart"))
					time.sleep(2)
					subprocess.call(("hciconfig", "hci0", "piscan"))
					data = "Name change requested."
					client_sock.send(data)
					raise KeyboardInterrupt

			except IOError:
				pass

			except KeyboardInterrupt:
				client_sock.close()
				server_sock.close()

	except KeyboardInterrupt:
		subprocess.call(("hciconfig", "hci0", "noscan"))
		if DEBUG:
			logger.info("Stop server")
