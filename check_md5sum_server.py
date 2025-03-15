import sys
import hashlib

FILE = sys.argv[1]
original_md5 = sys.argv[2]

with open(FILE, 'rb') as file_to_check:
    data = file_to_check.read()    
    md5_returned = hashlib.md5(data).hexdigest()

if original_md5 == md5_returned:
    print("MD5 verified.")
else:
    print("MD5 verification failed!.")
    print(original_md5, md5_returned)