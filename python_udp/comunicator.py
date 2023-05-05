# udp and network dependencies
import socket
import hashlib as hash


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

    packages = list()

    with open(FILE_NAME, "rb") as o_file:
        # send file name and start marker
        # package = u.create_packege(c.INFO_TYPE, None, FILE_NAME.encode("utf-8"))
        # u.send_package(sock, package, c.TARGET_ADRESS)

        # package = u.create_packege(c.MARKER_TYPE, None, c.START_MARKER)
        # u.send_package(sock, package, c.TARGET_ADRESS)

        # read data
        last = False
        while True:
            position = int(o_file.tell())
            package = u.create_packege(c.DATA_TYPE, position, o_file.read(c.DATA_SIZE))
            packages.append(package)
            hash_num.update(package[c.DATA_POS])

            if packages[-1][c.DATA_POS] == b"":
                packages.append(u.create_packege(c.MARKER_TYPE, None, c.END_MARKER))
                last = True
            
            # if sending window is full
            if len(packages) == c.SENDING_WINDOW or last:
                # send burst
                u.send_packages_burst(sock, packages, c.TARGET_ADRESS)
                packages = list()
                            
            if last:
                break

    # send file hash (sha256)
    hash_num = hash_num.digest()
    package = u.create_packege(c.INFO_TYPE, None, hash_num)
    u.send_package(sock, package, c.TARGET_ADRESS)


# RECIEVER =============================================================
elif side == "R":
    sock.bind(c.TARGET_ADRESS)
    hash_num = hash.sha256()

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
        packages = list()
        while True:
            try:
                package = u.recieve_package(c.PACKAGE_SIZE, sock)
            except TimeoutError:
                package = None
            if package[c.TYPE_POS] == c.MARKER_TYPE and package[c.DATA_POS] == c.END_MARKER:
                last = True
            packages.append(package)
                
            for pack in packages:
                pass
            
            if last:    
                break
            
            # if (package[c.DATA_POS] == c.SENDER_ERROR_MARKER) and (package[c.TYPE_POS] == c.MARKER_TYPE):
            #     print(c.ERROR_SENDER_ERROR)
            #     break

            # elif (package[c.DATA_POS] == c.END_MARKER) and (package[c.TYPE_POS] == c.MARKER_TYPE):
            #     break

            # else:
            #     recieved_f.seek(int.from_bytes(
            #         package[c.POSITION_POS], byteorder="big"))
            #     recieved_f.write(package[c.DATA_POS])
            #     hash_num.update(package[c.DATA_POS])

    # Recieve and compare hash
    hash_num = hash_num.digest()
    package = u.recieve_package_ack(c.PACKAGE_SIZE, sock)
    if package[c.DATA_POS] != hash_num:
        raise Exception("Hash is wrong!")


else:
    print("Exiting without doing anything...")

sock.close()
print("Done!")
