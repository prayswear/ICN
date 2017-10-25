import socket
import binascii
from packet import *
import hashlib
import time

a='c0a80264'
b=socket.inet_ntoa(binascii.a2b_hex(a))
print(b)
print(time.time())
