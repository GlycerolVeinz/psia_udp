import const
import socket
import binascii
from time import sleep


def add_crc(package):
    crc = binascii.crc32(package[const.CRC_SIZE : const.PACKAGE_SIZE])
    package[const.CRC_POS] = crc.to_bytes(const.CRC_SIZE, byteorder="big")

def add_id(package, id):
    if not hasattr(add_id, "id"):
        add_id.id = 0
    else:
        add_id.id += 1
    
    return add_id.id.to_bytes(const.ID_SIZE, byteorder="big")
    
def create_packege(type : str, position : int, data):
    package = list(range(const.PACKAGE_SIZE))
    package[const.TYPE_POS] = type
    package[const.POSITION_POS] = position.to_bytes(const.POSITION_SIZE, byteorder="big")
    package[const.DATA_POS] = data
    package[const.ID_POS] = add_id(package, add_id.id)
    
    return package

def recieve_package(size : int, sock : socket.socket):
    sock.settimeout(const.TIMEOUT)
    package = sock.recv(size)
    crc = binascii.crc32(package[const.CRC_POS : const.PACKAGE_SIZE])
    if crc == int.from_bytes(package[const.CRC_POS], byteorder="big"):
        return package
    else:
        return None

def send_package(sock : socket.socket, package, target_address : tuple):
    # add crc
    add_crc(package)
    # send package
    sock.sendto(package, target_address)
    
    # recieve acknowledge from receiver
    r_packet = recieve_package(const.PACKAGE_SIZE, sock)
    tries = 0
    while True:
        sleep(0.0001)
        
        if r_packet == None:
            # send package again (crc is wrong)
            sock.sendto(package, target_address)
        elif r_packet[const.TYPE_POS] != const.MARKER_TYPE:
            # send package again (package type is wrong)
            sock.sendto(package, target_address)
        elif r_packet[const.DATA_POS] == const.ACKNOWLEDGE_MARKER:
            # acknowledge is correct
            break
        else:
            # send package again (unknown error)
            sock.sendto(package, target_address)
        
        r_packet = recieve_package(const.PACKAGE_SIZE, sock)
        
        tries += 1
        if tries > const.MAX_TRIES:
            sock.close()
            package = create_packege(const.MARKER_TYPE, None, const.ERROR_MAX_TRIES)
            sock.sendto(package, target_address)
            raise Exception(const.ERROR_MAX_TRIES)
    
def recieve_package_ack(size : int, sock : socket.socket, target_adress = const.SENDER_ADRESS):
    sock.timeout(const.TIMEOUT)
    package = recieve_package(size, sock)
    
    while package == None:
        s_package = create_packege(const.MARKER_TYPE, None, const.DENIED_MARKER)
        send_package(sock, s_package, target_adress)
        
        package = recieve_package(size, sock)
    
    s_package = create_packege(const.MARKER_TYPE, None, const.ACKNOWLEDGE_MARKER)
    send_package(sock, s_package, target_adress)
    