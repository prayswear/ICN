import socket
import threading
import logging.config
from packet import *
import binascii
import time
import os
import datetime
import urllib.request
import urllib.parse

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')

LAN_UDP_MTU = 1472
STD_UDP_MTU = 548
UDP_MTU = LAN_UDP_MTU

temp_packet_dict = {}
ave_packet_recv_rate = 0


def notify_page(filepath, euid, na):
    params = urllib.parse.urlencode({'filePath': filepath, 'euid': euid, 'na': na})
    url = "http://127.0.0.1:8080/icn-api/v1/monitor/notify?%s" % params
    urllib.request.urlopen(url)


def packet_recv_rate():
    with open('recv_rate.txt', 'w') as fp:
        while True:
            global ave_packet_recv_rate
            fp.write(str(datetime.datetime.now()) + '  recv_rate: ' + str(ave_packet_recv_rate) + '\n')
            fp.flush()
            ave_packet_recv_rate = 0
            time.sleep(2)


def data_finish_handler(packet_id, address):
    logger.info('Recieve a packet from ' + str(address))
    #global ave_packet_recv_rate
    #total = temp_packet_dict[packet_id]['total']
    #ave_packet_recv_rate = (total - temp_packet_dict[packet_id]['count']) / total
    p = temp_packet_dict[packet_id]['icn_head']
    p.setTLV = binascii.a2b_hex('')
    p.payload = p.payload[:2] + temp_packet_dict[packet_id]['data']
    p.print_packet()
    del temp_packet_dict[packet_id]
    # reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # reply_socket.sendto('OK'.encode('utf-8'), address)
    content_euid = binascii.b2a_hex(p.payload)[2:34]
    with open('input.h264', 'wb') as f:
        f.write(p.payload)
        f.close()
    os.system('avconv -r 24 -i input.h264 -vcodec copy output.mp4 -y')
    filetime = str(int(time.time()))
    os.system('cp output.mp4 cam1_' + filetime + '.mp4')
    filepath = 'file:///home/lijq/PycharmProjects/ICN/packet/cam1_' + filetime + '.mp4'
    notify_page(filepath, content_euid, str(address[0]))


def timeout_handler(packet_id, address):
    start_time = time.time()
    while True:
        time_gap = time.time() - start_time
        if time_gap > 2:
            if packet_id in temp_packet_dict.keys():
                data_finish_handler(packet_id, address)
            break


def data_handler(data, address):
    top_n = 10
    logger.info('Recv UDP packet from: ' + str(address))
    p = ICNPacket()
    p.gen_from_hex(data)
    packet_id = binascii.b2a_hex(p.tlv[0:2])
    packet_length = int(binascii.b2a_hex(p.tlv[2:6]), 16)
    packet_seq = int(binascii.b2a_hex(p.tlv[6:8]), 16)
    print(binascii.b2a_hex(p.tlv))
    print(packet_id, ' ', packet_length, ' ', packet_seq)
    icn_type = p.payload[:2]
    payload = p.payload[2:len(p.payload)]
    DATA_SIZE_PER_UDP = UDP_MTU - p.header_len - len(icn_type)
    recv_times = 1
    if not packet_id in temp_packet_dict.keys():
        if packet_seq > top_n:
            logger.warning('drop an unused packet')
            return False
        else:
            temp_dict = {}
            #temp_dict['icn_head'] = p
            temp_data = binascii.a2b_hex('00' * packet_length)
            temp_dict['data'] = temp_data[0:packet_seq * DATA_SIZE_PER_UDP] + payload + \
                                temp_data[packet_seq * DATA_SIZE_PER_UDP + len(payload):packet_length]
            packet_num = packet_length / DATA_SIZE_PER_UDP
            if packet_num == int(packet_num):
                temp_dict['count'] = int(packet_num) * recv_times
            else:
                temp_dict['count'] = (int(packet_num) + 1) * recv_times
            #temp_dict['total'] = temp_dict['count']
            temp_packet_dict[packet_id] = temp_dict
            print(str(temp_packet_dict))
            # logger.info('packet_seq: ' + str(packet_seq))
            threading._start_new_thread(timeout_handler, (packet_id, address))
    else:
        temp_packet_dict[packet_id]['data'] = temp_packet_dict[packet_id]['data'][
                                              0:packet_seq * DATA_SIZE_PER_UDP] + payload + \
                                              temp_packet_dict[packet_id]['data'][
                                              packet_seq * DATA_SIZE_PER_UDP + len(payload):packet_length]
        # logger.info('packet_seq: ' + str(packet_seq))
    temp_packet_dict[packet_id]['count'] -= 1
    logger.info('count: ' + str(temp_packet_dict[packet_id]['count']))
    if temp_packet_dict[packet_id]['count'] == 0:
        data_finish_handler(temp_packet_dict[packet_id]['data'], address)


def start_data_server(address):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.bind(address)
    logger.info('start data server')
    threading._start_new_thread(packet_recv_rate, ())
    while True:
        data, client_address = data_socket.recvfrom(UDP_MTU)
        threading._start_new_thread(data_handler, (data, client_address))


def cmd_handler(data, address):
    logger.info('Recieve a packet from ' + str(address))
    p = ICNPacket()
    p.gen_from_hex(data)
    p.print_packet()
    # reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # reply_socket.sendto('OK'.encode('utf-8'), address)


def start_cmd_server(address):
    cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cmd_socket.bind(address)
    while True:
        data, address = cmd_socket.recvfrom(UDP_MTU)
        threading._start_new_thread(cmd_handler, (data, address))


if __name__ == '__main__':
    cmd_address = ('0.0.0.0', 35000)
    data_address = ('0.0.0.0', 36000)
    # start_cmd_server(cmd_address)
    start_data_server(data_address)
