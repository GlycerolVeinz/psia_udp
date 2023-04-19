import socket
import const as c
import util
# UDP SOCKET
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


side = input("Select side [S/R] (S - sender, R - receiver):")

if side == "S":
	
	
	FILE_NAME = input("Enter file name: ")

	# Open binary file
	with open(FILE_NAME, "rb") as o_file:
		sock.sendto(FILE_NAME.encode("utf-8"), (c.TARGET_IP, c.TARGET_PORT))
		sock.sendto(c.START_MARKER, (c.TARGET_IP, c.TARGET_PORT))

		data_package = o_file.read(c.DATA_SIZE)
		position = int(o_file.tell())

		while data_package:
			# Send data
			package = position.to_bytes(c.POSITION_SIZE, byteorder="big") + data_package
			util.package_send(sock, package)

			# Read next data
			data_package = o_file.read(c.DATA_SIZE)
			position = int(o_file.tell())

		sock.sendto(c.END_MARKER, (c.TARGET_IP, c.TARGET_PORT))
	

if side == "R":
	pass
