import sys
import hashlib

FILE = sys.argv[1]
print(hashlib.md5(open(FILE,'rb').read()).hexdigest())