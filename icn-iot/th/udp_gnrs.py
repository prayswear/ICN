import socket
from packet import *
import binascii
import time

udp_gnrs_ip = '192.168.44.148'
udp_gnrs_port = 8899

# udp_gnrs_ip = '192.168.47.16'
# udp_gnrs_port = 8899

# udp_gnrs_ip = '192.168.100.150'
# udp_gnrs_port = 8888

def gettime():
    return binascii.a2b_hex(hex(int(time.time()))[2:10])
def send_packet(dst_ip, dsp_port, packet):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_packet1(sock,dst_ip, dsp_port, packet)


def send_packet1(sock,dst_ip, dsp_port, packet):
    try:
        sock.sendto(packet,(dst_ip,dsp_port))
    except socket.error as e:
        logger.error(e)
    finally:
        pass
        # sock.close()


def udp_gnrs_reg(euid,na):
    print(na)
    packet = ICNPacket()
    packet.setHeader('b498dce7ea1f7a1a1b11a48dfef58303', 'b13ded0762217339428aba5d508ddf5c', '00')
    payload = binascii.a2b_hex('01'+euid) + socket.inet_aton(na) + gettime() + binascii.a2b_hex('02')
    print("PAYLOAD: ",payload)
    packet.setPayload(payload)
    packet.fill_packet()
    data = packet.grap_packet()
    print('##################################')
    print(data)
    #packet.print_packet()
    print('##################################')





    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.settimeout(2)
    s.bind(('0.0.0.0',9988))
    flag = 1
    while flag:
        try:
            # send_packet(s,udp_gnrs_ip, udp_gnrs_port, data)
            s.sendto(data,(udp_gnrs_ip,udp_gnrs_port))
            data123,address123 = s.recvfrom(1024)
            a=ICNPacket()
            a.gen_from_hex(data123)
            #a.print_packet()
            ppp = binascii.b2a_hex(a.payload).decode('utf-8')
            if ppp[0:2] == '02' and ppp[2:34] == euid and ppp[34:36] == '01':
                flag = 0
        except socket.timeout:
            print('***gnrs timeout retry***')
            pass
        finally:
            if flag == 0:
                s.close()
                return True
