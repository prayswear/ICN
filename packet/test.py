from packet import *
import binascii

a=b'123f'
print(len(a))

a = ICNPacket()
# src_guid = '0123456789abcdef0123456789abcdef12abcdef'
# dst_guid = 'affffffffffffffffffffffffffffffffffffffa'
# src_na = '87654321'
# dst_na = '12345678'
# a.setHeader(src_guid, dst_guid, src_na, dst_na, 'ee')
# a.tlv='abcdef'
# a.payload='dcba'
#
# a.fill_packet()
# b = a.grap_packet()
# print(b)
# print(len(b))
# print(binascii.b2a_hex(b))
#
# print('checksum: ' + str(a.check_checksum()))
# a.print_packet()
# b=b'\x01#Eg\x89\xab\xcd\xef\x01#Eg\x89\xab\xcd\xef\x12\xab\xcd\xef\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x124Vx\xee4$\x17'
b=b'\x01#Eg\x89\xab\xcd\xef\x01#Eg\x89\xab\xcd\xef\x12\xab\xcd\xef\xaf\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfa\x87eC!\x124Vx\xee7%\x16\xab\xcd\xef\xdc\xba'
a.gen_from_hex(b)
a.print_packet()
print(a.check_checksum())