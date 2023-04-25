import const
import socket
import binascii


def add_crc(package):
    crc = binascii.crc32(package)
    package[const.CRC_POS] = crc.to_bytes(const.CRC_SIZE, byteorder="big")

def create_packege(type, position, data):
    package = list(range(const.PACKAGE_SIZE))
    package[const.TYPE_POS] = type
    package[const.POSITION_POS] = position
    package[const.DATA_POS] = data
    return package

def send_package(sock : socket.socket, package, target_address : tuple):
    # add crc
    add_crc(package)
    # send package
    sock.sendto(package, target_address)
    
    
