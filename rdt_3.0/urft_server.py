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
FOR_TEST = True # ถ้าเปิดไว้จะให้ server loop รับไฟล์เรื่อยๆ

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

filename = None
file = None
max_file_size = -1

enable_duplicate = False # เปิด/ปิด การส่ง packet ซ้ำ
enable_lost = False # rdt 3.0 ใช้ไม่ได้ เปิด/ปิด การส่ง packet lost (packet ไปไม่ถึง server)
client_recive_init = False

error_count = 5
# ============================ Program ============================ #

def initial_connection(data: str, addr):
    global filename
    global max_file_size

    try:
        name, size = data.split("_!@#$%^&*_")
        filename = name.replace("./", "").replace(".\\", "")
        max_file_size = int(size)
        return filename
    except:
        return None

sock.bind(SERVER_ADDR)
sock.settimeout(30) # ตั้ง Timeout เผื่อ connection ค้าง
print(f"[Server] started at {UDP_IP}:{UDP_PORT}, waiting for connections...")

wait_for_ack = 0

while True:
    data, addr = sock.recvfrom(4096 + 8) # ขนาดของ Fragmented + Seq number
    decoded_data = data.decode(errors='ignore')

    if len(decoded_data.split("_!@#$%^&*_")) == 2 or max_file_size == -1:
        filename = initial_connection(decoded_data, addr)

        if file == None and filename != None:
            file = open(filename, "wb")
            if enable_duplicate :
                sock.sendto("__INITIAL_CONNECTION__".encode(), addr)
            sock.sendto("__INITIAL_CONNECTION__".encode(), addr)
            print("[Server] initial file name and size", filename, max_file_size, end="\n\n")
        continue

    seq_num = int(data[:8].decode())
    print("[Server] recive seq from client", seq_num)
    
    if file is not None:
        if seq_num != wait_for_ack:
            print(f"[Server] Not match ACK packet {wait_for_ack} ({file.tell()}) ignore...", end="\n\n")
            continue
        
        file.write(data[8:])
        wait_for_ack = 1 - seq_num

        if enable_lost and random.random() < 0.05:
            print(f"[Server] Simple lost packet {seq_num}", end="\n\n")
            continue
        
        sock.sendto(f"{seq_num}".encode(), addr)
        print(f"[Server] ack to client {seq_num}", end="\n\n")

        if enable_duplicate and random.random() < 0.8:
            print(f"[Server] Duplicate packet {seq_num}", end="\n\n")
            sock.sendto(f"{seq_num}".encode(), addr)

        print("[Server] write byte", file.tell(),"ack", seq_num)
        print()

        if file.tell() >= int(max_file_size):
            file.close()
            print(f"[Server] File {filename} received successfully!")
            
            # สำหรับทดสอบ
            if FOR_TEST:
                filename = None
                file = None
                max_file_size = -1
                wait_for_ack = 0
                print("Waiting for new file...")
            else:
                break

sock.close()