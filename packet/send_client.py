import socket
import threading
import logging.config
from packet import *
import binascii
import hashlib
import time

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')

LAN_UDP_MTU = 1472
STD_UDP_MTU = 548
UDP_MTU = LAN_UDP_MTU


def int2bytes(num, format):
    num_hex_str = hex(num).replace('0x', '')
    format_str = '0' * (format - len(num_hex_str)) + num_hex_str
    return binascii.a2b_hex(format_str)


def send_cmd_packet(data, address):
    if len(data) > LAN_UDP_MTU:
        return False
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, address)
    sock.settimeout(0.5)
    try:
        reply, remote_addr = sock.recvfrom(1024)
        logger.info(reply.decode('utf-8'))
    except socket.timeout:
        logger.warning('Timeout and no reply')
    finally:
        sock.close()
    sock.close()


def send_data_packet(data, address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    icn_head_hex = data[:36]
    icn_type = data[36:38]
    data_part = data[38:]
    icn_packet = ICNPacket()
    icn_packet.gen_from_hex(icn_head_hex)
    icn_packet.setTLV(binascii.a2b_hex('0000000000000000'))
    icn_packet.fill_head_len()
    DATA_SIZE_PER_UDP = UDP_MTU - icn_packet.header_len - len(icn_type)
    data_size = len(data_part)
    icn_file_id = binascii.a2b_hex(hashlib.sha1(data_part).hexdigest()[0:4])
    send_times = 1
    while send_times > 0:
        sent_size = 0
        point = 0
        count = 0
        while sent_size < data_size:
            remain_size = data_size - sent_size
            send_size = DATA_SIZE_PER_UDP if remain_size > DATA_SIZE_PER_UDP else remain_size
            icn_packet.setTLV(icn_file_id + int2bytes(data_size, 8) + int2bytes(count, 4))
            send_data = data[point:point + send_size]
            point += send_size
            sent_size += send_size
            count += 1
            icn_packet.fill_packet()
            icn_packet.setPayload(icn_type+send_data)
            sock.sendto(icn_packet.grap_packet(), address)
            if count==1:
                time.sleep(0.5)
        send_times -= 1
    sock.close()


def query_gnrs(euid):
    gnrs_reply_listen_port = 12321
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)
    sock.bind(('0.0.0.0', gnrs_reply_listen_port))
    result = None
    try:
        reply, gnrs_addr = sock.recvfrom(1024)
        p = ICNPacket()
        p.gen_from_hex(reply)
        payload = binascii.b2a_hex(p.payload).decode('utf-8')
        if payload[0:2] == '04' and payload[2:34] == euid:
            result = socket.inet_ntoa(payload[34:42])
    except socket.timeout:
        logger.warning('GNRS timeout...')
    finally:
        sock.close()
        return result

def block4ip(euid):
    result=None
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0.5)
    s.bind(('0.0.0.0', 12321))
    flag = 1
    while flag:
        try:
            addr = ('0.0.0.0', 12321)
            s.bind(addr)
            query_result, gnrs_addr = s.recvfrom(1024)
            a = ICNPacket()
            a.gen_from_hex(query_result)
            ppp = binascii.b2a_hex(a.payload).decode('utf-8')
            if ppp[0:2] == '04' and ppp[2:34] == euid:
                flag = 0
                result=socket.inet_ntoa(ppp[34:42])
        except socket.timeout:
            print('***gnrs timeout retry***')
        finally:
            if flag == 0:
                s.close()
        return result


if __name__ == '__main__':
    cmd_port = 35000
    data_port = 36000
    gnrs_addr = ('192.168.1.100', 8899)
    cam_euid = 'ab92b7014f2887ea05450143f4c9ad01'
    # query_packet = ICNPacket()
    # query_packet.setHeader('bf77ac7196110678d84d03687eab03fb', 'b13ded0762217339428aba5d508ddf5c', '00')
    # query_packet.setPayload(binascii.a2b_hex('03' + cam_euid + '00'))
    # query_packet.fill_packet()
    # query_packet.print_packet()
    # send_cmd_packet(query_packet.grap_packet(), (gnrs_addr))
    #cam_addr = (query_gnrs(cam_euid), cmd_port)

    cam_addr = ('192.168.1.21', cmd_port)

    while True:
        notify_address=('0.0.0.0',23333)
        notify_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        notify_socket.bind(notify_address)
        time.sleep(2)
        #notify_data,notify_addr=notify_socket.recvfrom(1024)
        print('recv notify reply')
        # with open('delayflag.txt','w') as fp:
        #     fp.write(str(time.time()))
        #     fp.flush()
        #     fp.close()
        #send_cmd_packet(query_data, (gnrs_addr))
        if not cam_addr == None:
            request_packet = ICNPacket()
            request_packet.setHeader('bf77ac7196110678d84d03687eab03fb', 'b13ded0762217339428aba5d508ddf5c', '00')
            request_packet.setPayload(binascii.a2b_hex('0dab92b7014f2887ea05450143f4c9ad01'))
            request_packet.fill_packet()
            request_data = request_packet.grap_packet()
            request_packet.print_packet()
            print(len(request_data))
            send_cmd_packet(request_data, cam_addr)

    # if not cam_addr[0] == None:
    #     request_packet = ICNPacket()
    #     request_packet.setHeader('bf77ac7196110678d84d03687eab03fb', 'b13ded0762217339428aba5d508ddf5c', '00')
    #     request_packet.setPayload(binascii.a2b_hex('0d' + cam_euid))
    #     request_packet.print_packet()
    #     send_cmd_packet(request_packet.grap_packet(), cam_addr)
    # else:
    #     logger.error('can not query GNRS!')
