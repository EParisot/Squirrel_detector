import os
import shutil
import subprocess
from bluetooth import *

SRC_FOLDER = "../out"
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
		
		shutil.make_archive("tmp/SQRT", 'zip', SRC_FOLDER)
			
		print("calling ", build_command(client_info[0], 
								OBEX_CHAN, 
								"tmp/SQRT.zip"))
		res = subprocess.call(build_command(client_info[0], 
								OBEX_CHAN, 
								"tmp/SQRT.zip").split(" "))
		print("Sent file %s with return code %s" % (f, res))

		# End connexion
		data = 'GoodBye!'

		client_sock.send(data)
		print("sending [%s]" % data)

	except IOError:
		pass

	except KeyboardInterrupt:
		client_sock.close()
		server_sock.close()
		print("disconnected")
		break
