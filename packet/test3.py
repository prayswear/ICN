import socket
import binascii
from packet import *
import hashlib

# addr=socket.inet_ntoa(binascii.a2b_hex('c0a802c5'))
# print(addr)
data=b'\xbfw\xacq\x96\x11\x06x\xd8M\x03h~\xab\x03\xfb\xb1=\xed\x07b!s9B\x8a\xba]P\x8d\xdf\\\x00$\x0e_\x03\xab\x92\xb7\x01O(\x87\xea\x05E\x01C\xf4\xc9\xad\x01\x00'
print(len(binascii.b2a_hex(data)))
print(len(data))
p=ICNPacket()
p.gen_from_hex(data[:36])
p.print_packet()

icn_file_id = binascii.a2b_hex(hashlib.sha1(data).hexdigest()[0:4])
print(len(icn_file_id))
