import const as c
import socket
import binascii


# FUNCTION =============================================================
def add_crc(package):
    crc = binascii.crc32(bytes(package[c.CRC_SIZE:c.PACKAGE_SIZE]))
    package[c.CRC_POS] = crc.to_bytes(c.CRC_SIZE, byteorder="big")
    return package

# FUNCTION =============================================================
def add_id(package):
    if not hasattr(add_id, "id"):
        add_id.id = 0
    else:
        add_id.id += 1
    
    return add_id.id.to_bytes(c.ID_SIZE, byteorder="big")

# FUNCTION ============================================================= 
def create_packege(type : str, position : int, data):
    package = bytearray(c.PACKAGE_SIZE)
    package[c.TYPE_POS] = type
    if position != None:
        package[c.POSITION_POS] = position.to_bytes(c.POSITION_SIZE, byteorder="big")
    package[c.DATA_POS] = data
    package[c.ID_POS] = add_id(package)
    package = add_crc(package)
    
    return package

# FUNCTION =============================================================
def recieve_package(size : int, sock : socket.socket):
    sock.settimeout(c.TIMEOUT)
    package = bytes(sock.recv(size))
    crc = binascii.crc32(bytes(package[c.CRC_SIZE : c.PACKAGE_SIZE]))
    if crc == int.from_bytes(package[c.CRC_POS], byteorder="big"):
        return package
    else:
        return None

# FUNCTION =============================================================
def send_package(sock : socket.socket, package : bytes, target_address : tuple):
    sock.sendto(bytes(package), target_address)
    r_packet = bytes()
    tries = 0
    
    while True:
        try:
            timed_out = False
            r_packet = recieve_package(c.PACKAGE_SIZE, sock)
        except TimeoutError:
            # send again if timeout
            timed_out = True
            sock.sendto(package, target_address)
            print("sended again")
    
    # recieve acknowledge from receiver
        if not timed_out:
            if r_packet == None:
                # send package again (crc is wrong)
                sock.sendto(package, target_address)
            elif r_packet[c.TYPE_POS] != c.MARKER_TYPE:
                # send package again (package type is wrong)
                sock.sendto(package, target_address)
            elif r_packet[c.DATA_POS] == c.ACKNOWLEDGE_MARKER:
                # acknowledge is correct
                break
            else:
                # send package again (unknown error)
                sock.sendto(package, target_address)
            
        tries += 1
        if tries > c.MAX_TRIES:
            package = create_packege(c.MARKER_TYPE, None, c.ERROR_SENDER_ERROR)
            sock.sendto(package, target_address)
            sock.close()
            raise Exception(c.ERROR_MAX_TRIES)
    
# FUNCTION =============================================================
def recieve_package_ack(size : int, sock : socket.socket, target_adress = c.SENDER_ADRESS):
    sock.settimeout(c.TIMEOUT)
    package = recieve_package(size, sock)
    
    while package == None:
        # sender failed
        if (package[c.TYPE_POS] == c.MARKER_TYPE) and (package[c.DATA_POS] == c.ERROR_SENDER_ERROR):
            sock.close()
            print(c.ERROR_SENDER_ERROR)
            exit()
        
        s_package = create_packege(c.MARKER_TYPE, None, c.DENIED_MARKER)
        sock.sendto(s_package, target_adress)
        
        package = recieve_package(size, sock)
    
    s_package = create_packege(c.MARKER_TYPE, None, c.ACKNOWLEDGE_MARKER)
    sock.sendto(s_package, target_adress)
    
    return package

