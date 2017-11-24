import socket
import threading
import logging.config
from packet import *
import binascii
import time
import os
import urllib.request
import urllib.parse

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')
DATA_SIZE_PER_UDP = 1024
temp_packet_dict = {}

def sseenndd(fpfp,idid1,idid2):
    params = urllib.parse.urlencode({'filePath': fpfp, 'euid': idid1, 'na': idid2})
    url = "http://192.168.47.16:8081/icn-api/v1/monitor/notify?%s" % params
    urllib.request.urlopen(url)
    # with urllib.request.urlopen(url) as f:
    #     print(f.read().decode('utf-8'))

def cmd_handler(data, address):
    logger.info('Recieve a packet from ' + str(address))
    p = ICNPacket()
    p.gen_from_hex(data)
    # p.print_packet()
    reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reply_socket.sendto('OK'.encode('utf-8'), address)
    # you can also call another func here



def data_finish_handler(data, address):
    logger.info('Recieve a packet from ' + str(address))
    p = ICNPacket()
    p.gen_from_hex(data)
    # p.print_packet()
    reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reply_socket.sendto('OK'.encode('utf-8'), address)
    f = open('input.h264', 'wb')
    f.write(p.payload)
    f.close()
    os.system('avconv -r 24 -i input.h264 -vcodec copy output.mp4 -y')
    os.system('cp -f output.mp4 /var/www/html/thisismp4.mp4')
    os.system('cp -f output.mp4 ./html/thisismp4.mp4')
    sseenndd('http://192.168.150.240/thisismp4.mp4','0dab92b7014f2887ea05450143f4c9ad01',str(address[0]))



def timeout_handler(packet_id, address):
    start_time = time.time()
    while True:
        timegap = time.time() - start_time
        if timegap > 2:
            if packet_id in temp_packet_dict.keys():
                data_finish_handler(temp_packet_dict[packet_id]['data'], address)
                del temp_packet_dict[packet_id]
            break


def data_handler(data, address):
    # logger.info('UDP packet from: ' + str(address))
    packet_id = binascii.b2a_hex(data[0:2])
    packet_length = int(binascii.b2a_hex(data[2:6]), 16)
    packet_seq = int(binascii.b2a_hex(data[6:8]), 16)
    data = data[8:len(data)]
    # print(packet_id, ' ', packet_length, ' ', packet_seq)
    if packet_seq == 0:
        temp_dict = {}
        # temp_dict['time'] = time.time()
        temp_data = binascii.a2b_hex('00' * packet_length)
        temp_dict['data'] = data + temp_data[len(data):packet_length]
        packet_num = packet_length / DATA_SIZE_PER_UDP
        if packet_num == int(packet_num):
            temp_dict['count'] = int(packet_num)
        else:
            temp_dict['count'] = int(packet_num) + 1
        temp_packet_dict[packet_id] = temp_dict
        print('packet_seq: ' + str(packet_seq))
        threading._start_new_thread(timeout_handler, (packet_id, address))
    else:
        if not packet_id in temp_packet_dict.keys():
            return
        else:
            temp_data = temp_packet_dict[packet_id]['data'][0:packet_seq * DATA_SIZE_PER_UDP] + data + \
                        temp_packet_dict[packet_id]['data'][packet_seq * DATA_SIZE_PER_UDP + len(data):packet_length]
            temp_packet_dict[packet_id]['data'] = temp_data
            print('packet_seq: ' + str(packet_seq))
    temp_packet_dict[packet_id]['count'] -= 1
    print('count: ' + str(temp_packet_dict[packet_id]['count']))
    # timegap = time.time() - temp_packet_dict[packet_id]['time']
    if temp_packet_dict[packet_id]['count'] == 0:
        data_finish_handler(temp_packet_dict[packet_id]['data'], address)
        del temp_packet_dict[packet_id]

def data_handler2(data, address):
    # logger.info('UDP packet from: ' + str(address))
    timestosend=2
    packet_id = binascii.b2a_hex(data[0:2])
    packet_length = int(binascii.b2a_hex(data[2:6]), 16)
    packet_seq = int(binascii.b2a_hex(data[6:8]), 16)
    data = data[8:len(data)]
    if packet_seq == 0:
        temp_dict = {}
        # temp_dict['time'] = time.time()
        temp_data = binascii.a2b_hex('00' * packet_length)
        temp_dict['data'] = data + temp_data[len(data):packet_length]
        packet_num = packet_length / DATA_SIZE_PER_UDP
        if packet_num == int(packet_num):
            temp_dict['count'] = int(packet_num)*timestosend-timestosend+1
        else:
            temp_dict['count'] = (int(packet_num) + 1)*timestosend-timestosend+1
        temp_packet_dict[packet_id] = temp_dict
        print('packet_seq: ' + str(packet_seq))
        threading._start_new_thread(timeout_handler, (packet_id, address))
    else:
        if not packet_id in temp_packet_dict.keys():
            return
        else:
            temp_data = temp_packet_dict[packet_id]['data'][0:packet_seq * DATA_SIZE_PER_UDP] + data + \
                        temp_packet_dict[packet_id]['data'][packet_seq * DATA_SIZE_PER_UDP + len(data):packet_length]
            temp_packet_dict[packet_id]['data'] = temp_data
            print('packet_seq: ' + str(packet_seq))
    temp_packet_dict[packet_id]['count'] -= 1
    print('count: ' + str(temp_packet_dict[packet_id]['count']))
    if temp_packet_dict[packet_id]['count'] == 0:
        data_finish_handler(temp_packet_dict[packet_id]['data'], address)
        del temp_packet_dict[packet_id]


def start_data_server(address):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.bind(address)
    print('start data server')
    while True:
        data, client_address = data_socket.recvfrom(DATA_SIZE_PER_UDP + 26)
        threading._start_new_thread(data_handler2, (data, client_address))


def data_trans(address):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.bind(address)
    print('start data server')
    packet_seq = 0
    while True:
        data, client_address = data_socket.recvfrom(DATA_SIZE_PER_UDP + 26)
        print(packet_seq)
        packet_id = binascii.b2a_hex(data[0:2])
        packet_length = int(binascii.b2a_hex(data[2:6]), 16)
        data = data[8:len(data)]
        temp_dict={}
        packet_num = packet_length / DATA_SIZE_PER_UDP
        if packet_seq==0:
            print('ok')
            if packet_num == int(packet_num):
                temp_dict['count'] = int(packet_num)
            else:
                temp_dict['count'] = int(packet_num) + 1
            temp_dict['data']=binascii.a2b_hex('00' * packet_length)
            temp_packet_dict[packet_id] = temp_dict
        print(temp_packet_dict[packet_id])
        temp_data = temp_packet_dict[packet_id]['data'][0:packet_seq * DATA_SIZE_PER_UDP] + data + \
                    temp_packet_dict[packet_id]['data'][packet_seq * DATA_SIZE_PER_UDP + len(data):packet_length]
        temp_packet_dict[packet_id]['data'] = temp_data
        packet_seq+=1

        temp_packet_dict[packet_id]['count'] -= 1
        if temp_packet_dict[packet_id]['count'] == 0 :
            data_finish_handler(temp_packet_dict[packet_id]['data'], client_address)
        sock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto('OK'.encode('utf-8'),client_address)



def start_cmd_server(address):
    cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cmd_socket.bind(address)

    while True:
        data, address = cmd_socket.recvfrom(DATA_SIZE_PER_UDP)
        threading._start_new_thread(cmd_handler, (data, address))


if __name__ == '__main__':
    cmd_server_address = ('127.0.0.1', 35000)
    # data_server_address = ('192.168.46.214', 36000)
    data_server_address = ('192.168.100.2', 36000)
    # start_cmd_server(cmd_server_address)
    flag3=0
    start_data_server(('0.0.0.0', 36000))
    # data_trans(data_server_address)
