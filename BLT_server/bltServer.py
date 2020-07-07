import os
import shutil
from unittest.mock import patch
import time
import subprocess
from bluetooth import *

SRC_FOLDER = "../out"
DST_FOLDER = "tmp"

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

while True:
	print("Waiting for connection on RFCOMM channel %d" % port)

	client_sock, client_info = server_sock.accept()
	print("Accepted connection from ", client_info)

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
		print("received [%s]" % data)
		if data.decode() == "send":
			# Zip folder
			with patch("os.path.isfile", side_effect=accept):
				zipFile = shutil.make_archive(os.path.join(DST_FOLDER, "SQRT_" + time.strftime("%Y%m%d_%H%M%S")), 'zip', SRC_FOLDER)
			print("calling ", build_command(client_info[0], 
									OBEX_CHAN, 
									os.path.join(DST_FOLDER, zipFile)))
			res = subprocess.call(build_command(client_info[0], 
									OBEX_CHAN, 
									os.path.join(DST_FOLDER, zipFile)).split(" "))
			print("Sent archive with return code %s" % res)
			# Clean tmp folder
			os.remove(os.path.join(DST_FOLDER, zipFile))
			# End connexion
			if res == 255:
				data = 'Sent: ' + os.path.basename(zipFile) + " done. exit"
			else:
				data = "Error sending archive. exit"
			client_sock.send(data)

		elif "name" in data.decode():
			print("change name to ")
			pass

	except IOError:
		pass

	except KeyboardInterrupt:
		client_sock.close()
		server_sock.close()
		print("disconnected")
		break
