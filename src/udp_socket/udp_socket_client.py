import os
import sys
import hashlib

from socket import *

from .utils import check_arguments, make_pkt
from .types import CLIENT

FileDescriptorOrPath = int | str | bytes | os.PathLike[str] | os.PathLike[bytes]

class UDPSocketClient:
    def __init__(self):
        self.__sock = socket(AF_INET, SOCK_DGRAM)

    def check_sum_md5(self, file: FileDescriptorOrPath) -> str:
        return hashlib.md5(open(file,'rb').read()).hexdigest()
    
    def run(self):
        file_path, ip, port = check_arguments(True)

        file = open(file_path)
        file_name = os.path.basename(file_path)

        ack = -1
        recv_ack = -1
        last_sending_bytes = 0

        while ack != 0:
            pkt = make_pkt(0, file_name)

            self.__sock.sendto(pkt, (ip, port))

            msg, _ = self.__sock.recvfrom(2048)
            
            ack = int(msg.decode())

        while True:
            last_sending_bytes = file.tell()
            chunk = file.read(2048)
            
            if ack != recv_ack:
                ack = recv_ack
                file.seek(last_sending_bytes)
                chunk = file.read(2048)
            
            if not chunk:
                break

            pkt = None

            if ack == 0:
                pkt = make_pkt(1, chunk)
                recv_ack = 1
            else:
                pkt = make_pkt(0, chunk)
                recv_ack = 0
            
            self.__sock.sendto(pkt, (ip, port))

            msg, _ = self.__sock.recvfrom(2048)

            ack = msg.decode()

        self.__sock.close()