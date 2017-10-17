from packet import *
import binascii
import logging.config
import time
import socket
import hashlib

def int2bytes(num, format):
    num_hex_str = hex(num).replace('0x', '')
    format_str = '0' * (format - len(num_hex_str)) + num_hex_str
    return binascii.a2b_hex(format_str)

p=ICNPacket()
p.setHeader('bf77ac7196110678d84d03687eab03fb', 'b13ded0762217339428aba5d508ddf5c', '00')
p.setPayload(binascii.a2b_hex('bf77ac7196110678d84d03687eab03fb'))
p.fill_packet()
p.print_packet()
p.setTLV(binascii.a2b_hex('0000000000000000'))
p.fill_head_len()
p.print_packet()

print(len(int2bytes(4,8)))



# icn_file_id = binascii.a2b_hex(hashlib.sha1('123456'.encode('utf-8')).hexdigest()[0:4])
# send_data = icn_file_id + int2bytes(5555, 8) + int2bytes(45, 4)
# print(len(send_data))
# addr=reply[1]
# p=ICNPacket()
# p.gen_from_hex(reply[0])
# p.print_packet()
