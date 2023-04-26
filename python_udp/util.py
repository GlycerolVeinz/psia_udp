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
    
def create_packege(type, position, data):
    package = list(range(const.PACKAGE_SIZE))
    package[const.TYPE_POS] = type
    package[const.POSITION_POS] = position
    package[const.DATA_POS] = data
    package[const.ID_POS] = add_id(package, add_id.id)
    
    return package

def recieve_package(size, sock : socket.socket):
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
    while True:
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
        
        sleep(0.0001)
        r_packet = recieve_package(const.PACKAGE_SIZE, sock)
    
