from packet import *
import binascii
import logging.config
import time
import socket
import hashlib

content_euid = 'ab92b7014f2887ea05450143f4c9ad01'
request_packet = ICNPacket()
request_packet.setHeader('bf77ac7196110678d84d03687eab03fb', 'b13ded0762217339428aba5d508ddf5c', '00')
request_packet.setPayload(binascii.a2b_hex('0d' + content_euid))
request_packet.fill_packet()
request_packet.print_packet()
p_hex=request_packet.grap_packet()
print(len(p_hex))
a=p_hex[:36]
b=request_packet.payload[1:17]
print(binascii.b2a_hex(b))
print(len(binascii.a2b_hex('09')))






