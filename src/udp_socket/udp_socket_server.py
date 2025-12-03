from io import BufferedWriter
import os
import hashlib

from socket import *
from .utils import is_ack

FileDescriptorOrPath = int | str | bytes | os.PathLike[str] | os.PathLike[bytes]

class UDPSocketServer:
    def __init__(self, port):
        self.__port: int = port
        self.__sock = socket(AF_INET, SOCK_DGRAM)

        self.__file: BufferedWriter|None = None

    def check_sum_md5(self, file: FileDescriptorOrPath, md5_original: str) -> bool:
        with open(file, 'rb') as file_to_check:
            data = file_to_check.read()    
            md5_returned = hashlib.md5(data).hexdigest()
            
        return md5_original == md5_returned
    
    def run(self):
        self.__sock.bind(('', self.__port))

        print("Server ready to receive port:",self.__port)

        while True:
            msg, addr = self.__sock.recvfrom(2049)
            decoded_msg = msg.decode()

            if not self.__file and is_ack(decoded_msg, 0):
                name = decoded_msg[1:]
                self.__file = open(name, "wb")
            else:
                self.__file.write(msg[1:])

            ack = decoded_msg[0]
            
            self.__sock.sendto(ack.encode(), addr)
            print("ACK", ack)