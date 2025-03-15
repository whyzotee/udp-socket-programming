import os
import random
import sys
from socket import *

if len(sys.argv) < 4:
    print("Error: argument dose not match pattern 'python urft_client.py filename server_ip server_port' \n")
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

enable_duplicate = False # เปิด/ปิด การส่ง packet ซ้ำ
enable_lost = False # เปิด/ปิด การส่ง packet lost (packet ไปไม่ถึง server)

time_out = 0.25 # Timeout 0.5 วิ
byte_data = 4096 # ขนาดของ packet ที่ตัดส่ง และ รอรับจาก server
# เวลารอ server ตอบกลับ
sock.settimeout(time_out)

# ============================ Program ============================ #

def get_response_from_server():
    try:
        msg, _ = sock.recvfrom(byte_data)
        return msg.decode()
    except:
        return False

def retransmit(seq_num, last_byte_send):
    retransmit_time = 0

    # สร้าง packet ที่ lost ไปตอนส่ง
    # current_bytes = byte_data if file.tell() == 0 else file.tell()
    
    # ลดลง 1 step ของการอ่านไฟล์
    file.seek(last_byte_send)
    data = file.read(byte_data)
    packet = f"{seq_num:08d}".encode() + data

    while retransmit_time < 5:
        print("[Client] Error timeout Retransmit... packet", file.tell(), last_byte_send)

        # Retransmit
        sock.sendto(packet, SERVER_ADDR)
        print(f"[Client] send {file.tell()} seq", seq_num)

        result = get_response_from_server()
        
        if result:
            print("[Client] Ack from server", result)
            return result
        
        retransmit_time += 1

    return None

def send_file_byte():
    seq_num = 0
    readed_file_bytes = 0
    last_byte_send = 0

    while readed_file_bytes < MAX_FILE_SIZE:
        last_byte_send = file.tell()
        data = file.read(byte_data)
        packet = f"{seq_num:08d}".encode() + data # สร้าง packet โดยนำ Seq number + Fragmented 

        # จำลอง Lost
        if enable_lost and (random.random() < 0.8):
            print(f"[Client] Packet {file.tell()} {seq_num} lost, not sending it.")
            result = retransmit(seq_num, last_byte_send)

            if result is None:
                print("[Client] Error sever not ack close connection")
                return
                
            ack = int(result)
            readed_file_bytes = file.tell()
            seq_num = 1 - ack
            continue
            
        # ส่ง packet ไปที่ Server
        sock.sendto(packet, SERVER_ADDR)
        print(f"[Client] send {file.tell()} seq", seq_num)

        # จำลอง Duplicate packet
        if enable_duplicate and random.random() < 0.8:
            print(f"[Client] Duplicate packet {seq_num}")
            sock.sendto(packet, SERVER_ADDR)

        result = get_response_from_server()
        
        if result == False:
            result = retransmit(seq_num, last_byte_send)

            # เช็คว่า Return ออกมาเป็น None การเชื่อมต่ออาจหลุดไปแล้ว
            if result is None:
                print("[Client] Error sever not ack close connection")
                break
        else:
            print("[Client] ACK from Server", result)
        
        if result == "__INITIAL_CONNECTION__":
            file.seek(last_byte_send)
            continue

        if int(result) != seq_num:
            print("[Client] Duplicate ack ignore...................", result)

            current_bytes = byte_data if file.tell() == 0 else file.tell()
            file.seek(current_bytes - byte_data)
            continue

        ack = int(result)
        readed_file_bytes = file.tell()
        seq_num = 1 - ack

    return readed_file_bytes
    
print("[Client] UDP target IP:", SERVER_ADDR, " File:", FILE)

# ================================================= Setting ================================================= #
file_setup = f"{FILE}_!@#$%^&*_{MAX_FILE_SIZE}".encode()

sock.sendto(file_setup, SERVER_ADDR)
init = get_response_from_server()

while init == False:
    print("[Client] No response from server resending...", file_setup)
    sock.sendto(file_setup, SERVER_ADDR)
    init = get_response_from_server()
    print("[Client] server response", init)

# print("[Client] No response from server resending...", file_setup)
# sock.sendto(file_setup, SERVER_ADDR)
# init = get_response_from_server()
# print("[Client] server response", init)
# =========================================== Initial Connection ============================================ #
seneded_byte = send_file_byte()
print()
print(seneded_byte, "Bytes sended", MAX_FILE_SIZE, "Original size")

sock.close()
