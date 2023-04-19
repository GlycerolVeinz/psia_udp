import socket

PACKAGE_SIZE = 1024
DATA_SIZE = 1020

TARGET_IP = "147.32.221.18"
TARGET_PORT = 5020

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Open binary file
with open("data.bin", "rb") as o_file:
    data_package = o_file.read(DATA_SIZE)
