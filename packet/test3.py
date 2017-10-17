import socket
import binascii

addr=socket.inet_ntoa(binascii.a2b_hex('c0a802c5'))
print(addr)
