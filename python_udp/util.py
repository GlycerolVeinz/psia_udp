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
    
    # recieve acknowledge from receiver
    r_packet, r_address = sock.recvfrom(const.PACKAGE_SIZE)
    
    while r_packet != const.ACKNOWLEDGE_MARKER:
        if r_packet == const.DENIED_MARKER:
            # send again if failed
            sock.sendto(package, target_address)
        elif r_packet == const.SENDER_ERROR_MARKER:
            print("Error: sender had an error")
            sock.close()
            exit()
        else:
            raise Exception("Error: unknown error")
        r_packet, r_address = sock.recvfrom(const.PACKAGE_SIZE)
    
