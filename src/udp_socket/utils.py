import sys
from io import TextIOWrapper

def check_arguments(isClient=False):
    if (isClient):
        if (len(sys.argv) != 4):
            print("Error: argument does not match pattern 'python urft_client.py filename server_ip server_port'")
            sys.exit()

        # File, IP, Port
        return (sys.argv[1], sys.argv[2], int(sys.argv[3]))

    if len(sys.argv) < 3:
        print("Error: argument does not match pattern 'python urft_server.py server_ip server_port' \n")
        sys.exit()
    
    # IP, Port
    return (sys.argv[1], int(sys.argv[2]))

def make_pkt(seq: int, data: str, checksum: str=None) -> bytes:
    return (str(seq) + data).encode()

def is_ack(rcvpkt:str, seq: int) -> bool:
    return int(rcvpkt[:1]) == seq
