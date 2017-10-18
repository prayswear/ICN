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
ICN_MTU = UDP_MTU - 36  # 36 is len of none-tlv icn head
ICN_TEMP_MTU = ICN_MTU - 8  # 8 is len of tlv
ICN_CONTENT_MTU = ICN_TEMP_MTU - 1 - 16  # 1 is icn type, 16 is content euid
icn_data_reply_type = '09'


def int2bytes(num, length):
    # length is the bytes you want to get
    num_hex_str = hex(num).replace('0x', '')
    format_str = '0' * (length * 2 - len(num_hex_str)) + num_hex_str
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


def send_data_packet(packet, address):
    # data is like icn_head + '09' + euid + realdata
    send_times = 1
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    content_euid_hex = packet.payload[1:17]
    temp_packet = ICNPacket()
    temp_packet.setHeader(packet.src_guid, packet.dst_guid, '00')
    DATA_SIZE_PER_UDP = ICN_CONTENT_MTU  # 1411
    data2send = packet.grap_packet()
    data_size = len(data2send)
    current_id = hashlib.sha1(data2send).hexdigest()[0:4]  # 2 bytes
    sent_size = 0
    point = 0
    count = 0
    while sent_size < data_size:
        remain_size = data_size - sent_size
        send_size = DATA_SIZE_PER_UDP if remain_size > DATA_SIZE_PER_UDP else remain_size
        temp_packet.setTLV(binascii.a2b_hex(current_id) + int2bytes(data_size, 4) + int2bytes(count, 2))
        send_data = data2send[point:point + send_size]
        point += send_size
        sent_size += send_size
        count += 1
        temp_packet.setPayload(binascii.a2b_hex(icn_data_reply_type) + content_euid_hex + send_data)
        temp_packet.fill_packet()
        logger.info(temp_packet.print_packet_without_payload())
        sock.sendto(temp_packet.grap_packet(), address)
        if count == 1:
            time.sleep(0.1)
    send_times -= 1
    while send_times > 0:
        sent_size = DATA_SIZE_PER_UDP
        point = DATA_SIZE_PER_UDP
        count = 1
        while sent_size < data_size:
            remain_size = data_size - sent_size
            send_size = DATA_SIZE_PER_UDP if remain_size > DATA_SIZE_PER_UDP else remain_size
            temp_packet.setTLV(binascii.a2b_hex(current_id) + int2bytes(data_size, 4) + int2bytes(count, 2))
            send_data = data2send[point:point + send_size]
            point += send_size
            sent_size += send_size
            count += 1
            temp_packet.setPayload(binascii.a2b_hex(icn_data_reply_type) + content_euid_hex + send_data)
            temp_packet.fill_packet()
            logger.info(temp_packet.print_packet_without_payload())
            sock.sendto(temp_packet.grap_packet(), address)
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


def start_request():
    cmd_port = 35000
    gnrs_addr = ('192.168.1.100', 8899)
    content_euid = 'ab92b7014f2887ea05450143f4c9ad01'
    query_packet = ICNPacket()
    query_packet.setHeader('bf77ac7196110678d84d03687eab03fb', 'b13ded0762217339428aba5d508ddf5c', '00')
    query_packet.setPayload(binascii.a2b_hex('03' + content_euid + '00'))
    query_packet.fill_packet()
    query_packet.print_packet()
    send_cmd_packet(query_packet.grap_packet(), gnrs_addr)
    content_na = (query_gnrs(content_euid), cmd_port)
    if not content_na[0] == None:
        logger.info('content_na is ' + str(content_na))
        request_packet = ICNPacket()
        request_packet.setHeader('bf77ac7196110678d84d03687eab03fb', 'b13ded0762217339428aba5d508ddf5c', '00')
        request_packet.setPayload(binascii.a2b_hex('0d' + content_euid))
        request_packet.fill_packet()
        request_packet.print_packet()
        send_cmd_packet(request_packet.grap_packet(), content_na)
    else:
        logger.error('can not query GNRS!')


def do_request_without_gnrs():
    cmd_port = 35000
    content_euid = 'ab92b7014f2887ea05450143f4c9ad01'
    content_na = ('192.168.1.21', cmd_port)
    request_packet = ICNPacket()
    request_packet.setHeader('bf77ac7196110678d84d03687eab03fb', 'b13ded0762217339428aba5d508ddf5c', '00')
    request_packet.setPayload(binascii.a2b_hex('0d' + content_euid))
    request_packet.fill_packet()
    request_packet.print_packet()
    send_cmd_packet(request_packet.grap_packet(), content_na)


if __name__ == '__main__':
    data_port = 36000
    # start_request()
    do_request_without_gnrs()
