import socket
from packet import *
import binascii
s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.settimeout(2)
s.bind(('0.0.0.0',12321))
flag = 1
euid = 'd' * 32
xx = 1
while flag:
    try:
        # send_packet(udp_gnrs_ip, udp_gnrs_port, data)
        data123,address123 = s.recvfrom(1024)
        #print(binascii.b2a_hex(data123))
        a=ICNPacket()
        a.gen_from_hex(data123)
        #a.print_packet()
        ppp = binascii.b2a_hex(a.payload).decode('utf-8')
        print(ppp[0:2] == '01')
        if ppp[0:2] == '01' and ppp[2:34] == euid and ppp[34:36] == '01':
            flag = 0
    except socket.timeout:
        # send_packet(udp_gnrs_ip, udp_gnrs_port, data)
        print('老师姐喵了 %d 次'%xx)
        xx += 1
    finally:
        if flag == 0:
            s.close()