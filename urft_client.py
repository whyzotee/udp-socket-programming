import os
import sys
import random
from socket import *

if len(sys.argv) < 4:
    print("Error: argument does not match pattern 'python urft_client.py filename server_ip server_port' \n")
    sys.exit()

# ============================ Setup ============================ #

UDP_IP = sys.argv[2]
UDP_PORT = int(sys.argv[3])
SERVER_ADDR = (UDP_IP, UDP_PORT)

FILE_PATH = sys.argv[1]
FILE = os.path.basename(FILE_PATH)
MAX_FILE_SIZE = os.path.getsize(FILE_PATH)

sock = socket(AF_INET, SOCK_DGRAM)
file = open(FILE_PATH, "rb")

enable_duplicate = False  # เปิด/ปิด การส่ง packet ซ้ำ
enable_lost = False  # เปิด/ปิด การส่ง packet lost (packet ไปไม่ถึง server)
error_rate = 0.8

time_out = 0.25  # Timeout 0.25 วิ
byte_data = 4096  # ขนาดของ packet ที่ตัดส่ง และ รอรับจาก server
sock.settimeout(time_out)

# ============================ Program ============================ #
last_ack = None
readed_file_bytes = 0

def get_response_from_server():
    global last_ack
    try:
        msg, _ = sock.recvfrom(byte_data)
        ack = msg.decode()

        if ack == last_ack:
            print("[Client] Duplicate ACK received:", ack)
            return get_response_from_server()

        last_ack = ack
        return ack
    except:
        return "TIME_OUT"

def retransmit(seq_num, last_byte_send):
    global last_ack
    global readed_file_bytes
    retransmit_time = 0
   
    # สร้าง packet ที่ lost ไปตอนส่ง
    file.seek(last_byte_send)
    data = file.read(byte_data)
    packet = f"{seq_num:08d}".encode() + data
    readed_file_bytes = file.tell()

    ack = None

    while (isinstance(ack, str) or ack == None):
        sock.sendto(packet, SERVER_ADDR)
        print("[Client] Error timeout Retransmit... packet", last_byte_send, "seq", seq_num)

        ack = get_response_from_server()
        
        if isinstance(ack, str) and ack.isdigit():
            print("[Client] Retransmit Ack from server", ack, end="\n\n")
            return ack
        
        retransmit_time += 1
        print("[Client] Retry ", retransmit_time)

        if retransmit_time >= 5:
            print("[Client] No many server ack close connection", retransmit_time)
            break

    print("[Client] Error: Retransmit failed after multiple retries")
    return None

def send_file_byte():
    global last_ack
    global readed_file_bytes

    seq_num = 1
    last_byte_send = 0

    while readed_file_bytes < MAX_FILE_SIZE:
        last_byte_send = file.tell()
        data = file.read(byte_data)
        packet = f"{seq_num:08d}".encode() + data # สร้าง packet โดยนำ Seq number + Fragmented 

        # จำลอง Lost
        if enable_lost and random.random() < error_rate:
            print("[Client] simple lost")
        else:
            # ส่ง packet ไปที่ Server
            sock.sendto(packet, SERVER_ADDR)
            print(f"[Client] send {file.tell()} seq", seq_num)

        # จำลอง Duplicate packet
        if enable_duplicate and random.random() < error_rate:
            print(f"[Client] Duplicate packet {seq_num}")
            sock.sendto(packet, SERVER_ADDR)

        result = get_response_from_server()

        if result == "TIME_OUT":
            print("[Client] Timeout or Initial connection issue, retransmitting")
            result = retransmit(seq_num, last_byte_send)

        if result is None:
            print("[Client] Error server not ack, close connection")
            break

        print("[Client] ACK from Server", result, end="\n\n")

        last_ack = result
        ack = int(result)

        # ตรวจสอบว่า ack ตรงกับ seq_num หรือไม่
        if ack != seq_num:
            print(f"[Client] Error: ACK {ack} does not match expected seq {seq_num}. Retransmitting...")
            result = retransmit(seq_num, last_byte_send)
            continue

        readed_file_bytes = file.tell()
        seq_num = 1 - ack  # สลับ seq

    return readed_file_bytes

print("[Client] UDP target IP:", SERVER_ADDR, " File:", FILE, end="\n\n")

# ================================================= Setting ================================================= #
file_setup = f"{FILE}_!@#$%^&*_{MAX_FILE_SIZE}".encode()
packet = f"{0:08d}".encode() + file_setup

sock.sendto(packet, SERVER_ADDR)

if enable_duplicate and random.random() < error_rate:
    sock.sendto(packet, SERVER_ADDR)

init = get_response_from_server()

error_count = 0
while init == "TIME_OUT" and error_count <= 10:
    print("[Client] No response from server resending...", packet)
    sock.sendto(packet, SERVER_ADDR)
    init = get_response_from_server()
    print("[Client] server response", init)
    error_count += 1

last_ack = init
# =========================================== Initial Connection ============================================ #
seneded_byte = send_file_byte()
print()
print(seneded_byte, "Bytes sended", MAX_FILE_SIZE, "Original size")

sock.close()
