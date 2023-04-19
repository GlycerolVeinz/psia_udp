import const
import socket

def package_send(socket, package):
    if len(package) > const.PACKAGE_SIZE:
        socket.sendto(const.SENDER_ERROR_MARKER, (const.TARGET_IP, const.TARGET_PORT))
        raise Exception(const.ERROR_PACKAGE_SIZE + package[:4].hex())
    else:
        socket.sendto(package, (const.TARGET_IP, const.TARGET_PORT))