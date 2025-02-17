import sys
import socket

def main():
    if len(sys.argv) < 3:
        print("Error: argument dose not match pattern 'python urft_server.py server_ip server_port' \n")
        return
    
    UDP_IP = sys.argv[1]
    UDP_PORT = int(sys.argv[2])
    SERVER_ADDR = (UDP_IP, UDP_PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(SERVER_ADDR)

    print("Server ready to received message \n")

    initial = False

    max_file_size = 0
    # ================================================= Setting ================================================= #
    f = None

    while True:
        data, addr = sock.recvfrom(4096)

        if not initial:
            for msg in data.decode().split():
                if "file::" in msg:
                    f = open(f"{msg.replace("file::", "r_")}", "wb")
                if msg.isdigit():
                        max_file_size = int(msg)
                        initial = True
                        sock.sendto("ok!".encode(), addr)
        else:
            recived_file_size = f.tell()
            if recived_file_size >= max_file_size or "end-of-send-file" in data.decode():
                f.close()
                print(f"Recived data {recived_file_size} Bytes")
                break
            
            f.write(data)
            sock.sendto("Recived 4096 bytes data!".encode(), addr)

    initial = False

if __name__ == "__main__":
    main()