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
    FILE_NAME = "big_space.png"

    sock.bind(c.SENDER_ADRESS)
    hash_num = hash.sha256()

    packages = list()

    with open(FILE_NAME, "rb") as o_file:
        # send file name and start marker
        package = u.create_packege(c.INFO_TYPE, None, FILE_NAME.encode("utf-8"))
        u.send_package(sock, package, c.TARGET_ADRESS)

        package = u.create_packege(c.MARKER_TYPE, None, c.START_MARKER)
        u.send_package(sock, package, c.TARGET_ADRESS)

        # read and send data
        last = False
        reading = True
        tries = 0
        end_package = None
        while True:
            # read data
            if len(packages) != c.SENDING_WINDOW and reading:
                tries = 0
                position = int(o_file.tell())
                package = u.create_packege(c.DATA_TYPE, position, o_file.read(c.DATA_SIZE))
                hash_num.update(package[c.DATA_POS])

                
                if (package[c.DATA_POS] == b""):
                    end_package = u.create_packege(c.MARKER_TYPE, None, c.END_MARKER)
                    packages.append(end_package)
                    reading = False
                else:
                    packages.append(package)
                
            
            # send data
            for pack in packages:
                sock.sendto(pack, c.TARGET_ADRESS)
            
                # get acknowledge
                try:
                    r_package = u.recieve_package(c.PACKAGE_SIZE, sock, 0.1)
                except TimeoutError:
                    r_package = None
                    
                if r_package and (r_package[c.TYPE_POS] == c.MARKER_TYPE) and (r_package[c.DATA_POS] == c.ACKNOWLEDGE_MARKER) and (r_package[c.ID_POS] in [x[c.ID_POS] for x in packages]):
                    if end_package and (r_package[c.ID_POS] == end_package[c.ID_POS]):
                        last = True
                    packages = [x for x in packages if x[c.ID_POS] != r_package[c.ID_POS]]
                
            
            tries += 1
            if tries == c.MAX_TRIES:
                # TODO send error message
                sock.close()
                raise Exception(c.ERROR_MAX_TRIES)
                                   
            if last and len(packages) == 0:
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
        last = False
        while True:
            # recieve package 
            tries = 0
            try:
                package = u.recieve_package(c.PACKAGE_SIZE, sock, 0.1)
                if (package is None):
                    s_package = u.create_packege(c.MARKER_TYPE, None, c.DENIED_MARKER)
                    sock.sendto(s_package, c.SENDER_ADRESS)
                
                elif (package[c.TYPE_POS] == c.MARKER_TYPE) and (package[c.DATA_POS] == c.SENDER_ERROR_MARKER):
                    sock.close()
                    exit(c.ERROR_SENDER_ERROR)
                
                elif (package[c.TYPE_POS] == c.MARKER_TYPE) and (package[c.DATA_POS] == c.END_MARKER):
                    last = True
                
                elif (package[c.TYPE_POS] != c.DATA_TYPE):
                    s_package = u.create_packege(c.MARKER_TYPE, None, c.DENIED_MARKER)
                    sock.sendto(s_package, c.SENDER_ADRESS)
                                    
            except TimeoutError:
                tries += 1


            
            # send acknowledge
            s_package = u.create_packege(c.MARKER_TYPE, None, c.ACKNOWLEDGE_MARKER, id = package[c.ID_POS])    
            sock.sendto(s_package, c.SENDER_ADRESS)    
            
            # write data to file
            if package[c.DATA_POS] != c.END_MARKER:
                recieved_f.seek(int.from_bytes(package[c.POSITION_POS], byteorder="big"))
                recieved_f.write(package[c.DATA_POS])
                    
                    
            if tries == c.MAX_TRIES:
                sock.close()
                raise Exception(c.ERROR_MAX_TRIES)
            
            if last:    
                break
        
    # Compare hash
    with open("output_" + file_name, "rb") as tmp:
        hash_num.update(tmp.read())
        
    hash_num = hash_num.digest()
    package = u.recieve_package_ack(c.PACKAGE_SIZE, sock)
    if package[c.DATA_POS] != hash_num:
        raise Exception("Hash is wrong!")


else:
    print("Exiting without doing anything...")

sock.close()
print("Done!")
