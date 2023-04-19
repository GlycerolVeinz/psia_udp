import socket
import const as c
import util

# UDP SOCKET
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


side = input("Select side [S/R] (S - sender, R - receiver):")

if side == "S":
    sock.bind(c.SENDER_ADRESS)
    FILE_NAME = input("Enter file name: ")

    # Open binary file
    with open(FILE_NAME, "rb") as o_file:
        sock.sendto(FILE_NAME.encode("utf-8"), c.TARGET_ADRESS)
        sock.sendto(c.START_MARKER, c.TARGET_ADRESS)

        data_package = o_file.read(c.DATA_SIZE)
        position = int(o_file.tell())

        while data_package:
            # Send data
            package = position.to_bytes(c.POSITION_SIZE, byteorder="big") + data_package
            util.package_send(sock, package)

            # Read next data
            data_package = o_file.read(c.DATA_SIZE)
            position = int(o_file.tell())

        sock.sendto(c.END_MARKER, c.TARGET_ADRESS)

elif side == "R":
	sock.bind(c.TARGET_ADRESS)
	
	file_name, sender_address = sock.recvfrom(c.PACKAGE_SIZE)
	file_name = file_name.decode("utf-8")

	with open(file_name, "wb") as recieved_f:
		package, sender_address = sock.recvfrom(c.PACKAGE_SIZE)
  
		if package != c.START_MARKER:
			raise Exception(c.ERROR_START_MARKER)

		while package != c.END_MARKER:
			package, sender_address = sock.recvfrom(c.PACKAGE_SIZE)

			if package == c.SENDER_ERROR_MARKER:
				print(c.ERROR_SENDER_ERROR)
				exit()

			elif package != c.END_MARKER:
				recieved_f.write(package[c.POSITION_SIZE:])

else:
	print("Exiting without doing anything...")

sock.close()
print("Done!")