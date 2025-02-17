import os
import sys
from socket import *

def main():
    if len(sys.argv) < 4:
        print("Error: argument dose not match pattern 'python urft_client.py filename server_ip server_port' \n")
        return
    
    UDP_IP = sys.argv[2]
    UDP_PORT = int(sys.argv[3])
    SERVER_ADDR = (UDP_IP, UDP_PORT)

    FILE = sys.argv[1]
    MAX_FILE_SIZE = os.path.getsize(FILE)

    sock = socket(AF_INET, SOCK_DGRAM)

    print("UDP target IP: ", SERVER_ADDR)

    # ================================================= Setting ================================================= #

    sock.sendto(f"client ready to send file::{FILE} {MAX_FILE_SIZE} bytes of data".encode(), SERVER_ADDR)

    modifiedMessage, serverAddress = sock.recvfrom(1024)
    print(modifiedMessage.decode())

    f = open(FILE, "rb")
    
    readed_file_bytes = 0

    # =========================================== Initial Connection ============================================ #

    while readed_file_bytes < MAX_FILE_SIZE:
        data = f.read(4096)
        sock.sendto(data, SERVER_ADDR)
        readed_file_bytes = f.tell()

    print(readed_file_bytes, " Bytes sended")

    sock.sendto("end-of-send-file 200".encode(), SERVER_ADDR)
    sock.close()

if __name__ == "__main__":
    main()