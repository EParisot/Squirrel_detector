import os
import shutil
import time
import subprocess
from bluetooth import *

SRC_FOLDER = "../out"
DST_FOLDER = "tmp"
OBEX_CHAN = 12

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

while True:
	print("Waiting for connection on RFCOMM channel %d" % port)

	client_sock, client_info = server_sock.accept()
	print("Accepted connection from ", client_info)

	try:
		data = client_sock.recv(1024)
		if len(data) == 0:
			continue
		print("received [%s]" % data)
		
		# Zip folder
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
		print(data)

	except IOError:
		pass

	except KeyboardInterrupt:
		client_sock.close()
		server_sock.close()
		print("disconnected")
		break
