import sys
import socket
import random

if len(sys.argv) < 3:
    print("Error: argument does not match pattern 'python urft_server.py server_ip server_port' \n")
    sys.exit()

# ============================ Setup ============================ #

UDP_IP = sys.argv[1]
UDP_PORT = int(sys.argv[2])
SERVER_ADDR = (UDP_IP, UDP_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

filename = None
file = None
max_file_size = -1
error_rate = 0.5

enable_duplicate = True # เปิด/ปิด การส่ง packet ซ้ำ
enable_lost = False # rdt 3.0 ใช้ไม่ได้ เปิด/ปิด การส่ง packet lost (packet ไปไม่ถึง server)
client_recive_init = False

error_count = 5
# ============================ Program ============================ #
sock.bind(SERVER_ADDR)
sock.settimeout(30) # ตั้ง Timeout เผื่อ connection ค้าง
print(f"[Server] started at {UDP_IP}:{UDP_PORT}, waiting for connections...")

wait_for_ack = 0

init_count = 0

while init_count < error_count:
    data, addr = sock.recvfrom(4096 + 8) # ขนาดของ Fragmented + Seq number
    decoded_data = data.decode(errors='ignore')

    if len(decoded_data.split("_!@#$%^&*_")) == 2 and max_file_size == -1:
        name, size = decoded_data.split("_!@#$%^&*_")
        filename = name.replace("./", "").replace(".\\", "")
        file = open(filename, "wb")
        
        max_file_size = int(size)

        sock.sendto("__INITIAL_CONNECTION__".encode(), addr)

        if enable_duplicate:
            sock.sendto("__INITIAL_CONNECTION__".encode(), addr)
            print("[Server] send duplicate init")

        print("[Server] initial file name and size", filename, max_file_size, end="\n\n")
        break
 
    init_count += 1

while file.tell() < max_file_size:
    data, addr = sock.recvfrom(4096 + 8) # ขนาดของ Fragmented + Seq number
    decoded_data = data.decode(errors='ignore')

    if len(decoded_data.split("_!@#$%^&*_")) == 2:
        continue

    seq_num = int(data[:8].decode())
    print("[Server] recive seq from client", seq_num)
    
    if seq_num == wait_for_ack:
        if enable_lost and random.random() < error_rate:
            print(f"[Server] Simple lost packet {seq_num}", end="\n\n")
        else:
            sock.sendto(f"{seq_num}".encode(), addr)
            print(f"[Server] ack to client {seq_num}", file.tell())

            if enable_duplicate and random.random() < error_rate:
                print(f"[Server] Duplicate packet {seq_num}", end="\n\n")
                sock.sendto(f"{seq_num}".encode(), addr)

            print()

        file.write(data[8:])
        wait_for_ack = 1 - seq_num
    else:
        sock.sendto(f"{seq_num}".encode(), addr)
        print(f"[Server] ack to client {seq_num}", file.tell(), end="\n\n")
    
sock.close()