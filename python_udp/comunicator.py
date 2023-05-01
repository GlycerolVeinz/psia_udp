# udp and network dependencies
import socket
import hashlib as hash
import binascii

# my libraries
import const as c
import util as u


# UDP SOCKET
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

side = input("Select side [S/R] (S - sender, R - receiver):")

# SENDER =============================================================
if side == "S":
    # FILE_NAME = input("Enter file name: ")
    FILE_NAME = "vit_small.ppm"
    
    sock.bind(c.SENDER_ADRESS)
    hash_num = hash.sha256()

    with open(FILE_NAME, "rb") as o_file:
        # send file name and start marker
        package = u.create_packege(c.INFO_TYPE, None, FILE_NAME.encode("utf-8"))
        u.send_package(sock, package, c.TARGET_ADRESS)
        
        package = u.create_packege(c.MARKER_TYPE, None, c.START_MARKER)
        u.send_package(sock, package, c.TARGET_ADRESS)

        # read first data (if there is none, while loop will not be executed)
        position = int(o_file.tell())
        package = u.create_packege(c.DATA_TYPE, position, o_file.read(c.DATA_SIZE))
        hash_num.update(package[c.DATA_POS])

        while package[c.DATA_POS]:
            # Send package (this check is only for debuging)
            if len(package) > c.PACKAGE_SIZE:
                package = u.create_packege(c.MARKER_TYPE, None, c.SENDER_ERROR_MARKER)
                u.send_package(sock, package, c.TARGET_ADRESS)
                raise Exception(c.ERROR_PACKAGE_SIZE + str(len(package)))
            else:
                u.send_package(sock, package, c.TARGET_ADRESS)
            
            # Read next data
            position = int(o_file.tell())
            package = u.create_packege(c.DATA_TYPE, position, o_file.read(c.DATA_SIZE))
            hash_num.update(package[c.DATA_POS])

    # send end marker
    package = u.create_packege(c.MARKER_TYPE, None, c.END_MARKER)
    u.send_package(sock, package, c.TARGET_ADRESS)
    
    # send file hash (sha256)
    hash_num = hash_num.digest()
    package = u.create_packege(c.INFO_TYPE, None, hash_num)
    u.send_package(sock, package, c.TARGET_ADRESS)
  


# RECIEVER =============================================================
elif side == "R":
    sock.bind(c.TARGET_ADRESS)

    # Recieve file name
    package = u.recieve_package_ack(c.PACKAGE_SIZE, sock) 
    file_name = (package[c.DATA_POS]).decode("utf-8")

    # Create a file, where name is taken from sender
    with open("output_" + file_name, "wb") as recieved_f:
        # Recieve start marker
        package = u.recieve_package_ack(c.PACKAGE_SIZE, sock)

        if (package[c.DATA_POS] != c.START_MARKER) and (package[c.TYPE_POS] == c.MARKER_TYPE):
            sock.close()
            raise Exception(c.ERROR_START_MARKER)

        # Write data
        while True:
            package = u.recieve_package_ack(c.PACKAGE_SIZE, sock)
            
            if (package[c.DATA_POS] == c.SENDER_ERROR_MARKER) and (package[c.TYPE_POS] == c.MARKER_TYPE):
                print(c.ERROR_SENDER_ERROR)
                break

            elif package == c.END_MARKER:
                break
            
            else:
                recieved_f.seek(int.from_bytes(package[c.POSITION_POS], byteorder="big"))
                recieved_f.write(package[c.DATA_POS])

else:
    print("Exiting without doing anything...")

sock.close()
print("Done!")