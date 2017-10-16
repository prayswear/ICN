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
DATA_SIZE_PER_UDP = 1024
temp_packet_dict = {}
ave_packet_recv_rate = 0

def sseenndd(fpfp,idid1,idid2):
    params = urllib.parse.urlencode({'filePath': fpfp, 'euid': idid1, 'na': idid2})
    url = "http://127.0.0.1:8080/icn-api/v1/monitor/notify?%s" % params
    urllib.request.urlopen(url)
    # with urllib.request.urlopen(url) as f:
    #     print(f.read().decode('utf-8'))




#/home/lijq/PycharmProjects/ICN/packet/*.mp4
def cmd_handler(data, address):
    logger.info('Recieve a packet from ' + str(address))
    p = ICNPacket()
    p.gen_from_hex(data)
    p.print_packet()
    reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reply_socket.sendto('OK'.encode('utf-8'), address)


def data_finish_handler(data, address):
    logger.info('Recieve a packet from ' + str(address))
    p = ICNPacket()
    p.gen_from_hex(data)
    p.print_packet()
    reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reply_socket.sendto('OK'.encode('utf-8'), address)
    f = open('input.h264', 'wb')
    f.write(p.payload)
    f.close()
    os.system('avconv -r 24 -i input.h264 -vcodec copy output.mp4 -y')
    filetime=str(int(time.time()))
    os.system('cp output.mp4 cam1_'+filetime+'.mp4')
    filepath='/home/lijq/PycharmProjects/ICN/packet/cam1_'+filetime+'.mp4'
    sseenndd(filepath, '0dab92b7014f2887ea05450143f4c9ad01', str(address[0]))


def timeout_handler(packet_id, address):
    start_time = time.time()
    while True:
        timegap = time.time() - start_time
        if timegap > 2:
            if packet_id in temp_packet_dict.keys():
                data_finish_handler(temp_packet_dict[packet_id]['data'], address)
                global ave_packet_recv_rate
                total = temp_packet_dict[packet_id]['total']
                ave_packet_recv_rate = (total - temp_packet_dict[packet_id]['count']) / total
                del temp_packet_dict[packet_id]
            break


def data_handler(data, address):
    # logger.info('UDP packet from: ' + str(address))
    packet_id = binascii.b2a_hex(data[0:2])
    packet_length = int(binascii.b2a_hex(data[2:6]), 16)
    packet_seq = int(binascii.b2a_hex(data[6:8]), 16)
    data = data[8:len(data)]
    times = 1
    # print(packet_id, ' ', packet_length, ' ', packet_seq)
    if packet_seq == 0:
        record_delay(packet_id)
        temp_dict = {}
        # temp_dict['time'] = time.time()
        temp_data = binascii.a2b_hex('00' * packet_length)
        temp_dict['data'] = data + temp_data[len(data):packet_length]
        packet_num = packet_length / DATA_SIZE_PER_UDP

        if packet_num == int(packet_num):
            temp_dict['count'] = int(packet_num) * times - times + 1
        else:
            temp_dict['count'] = (int(packet_num) + 1) * times - times + 1
        temp_dict['total'] = temp_dict['count']
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
        global ave_packet_recv_rate
        ave_packet_recv_rate = 1
        data_finish_handler(temp_packet_dict[packet_id]['data'], address)
        del temp_packet_dict[packet_id]

def record_delay(packet_id):
    with open('delayflag.txt', 'r') as f:
        start_time = float(f.readline())
        f.close()
    with open('delay_record.txt', 'a') as f2:
        f2.write(str(datetime.datetime.now()) + '  delay of packet:' +packet_id.decode('utf-8')+' is '+str(time.time()-start_time)+'\n')
        f2.flush()
        f2.close()

def start_data_server(address):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.bind(address)
    print('start data server')
    threading._start_new_thread(packet_recv_rate,())
    while True:
        data, client_address = data_socket.recvfrom(DATA_SIZE_PER_UDP + 26)
        threading._start_new_thread(data_handler, (data, client_address))

'''
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
        temp_dict = {}
        packet_num = packet_length / DATA_SIZE_PER_UDP
        if packet_seq == 0:
            print('ok')
            if packet_num == int(packet_num):
                temp_dict['count'] = int(packet_num)
            else:
                temp_dict['count'] = int(packet_num) + 1
            temp_dict['data'] = binascii.a2b_hex('00' * packet_length)
            temp_packet_dict[packet_id] = temp_dict
        print(temp_packet_dict[packet_id])
        temp_data = temp_packet_dict[packet_id]['data'][0:packet_seq * DATA_SIZE_PER_UDP] + data + \
                    temp_packet_dict[packet_id]['data'][packet_seq * DATA_SIZE_PER_UDP + len(data):packet_length]
        temp_packet_dict[packet_id]['data'] = temp_data
        packet_seq += 1

        temp_packet_dict[packet_id]['count'] -= 1
        if temp_packet_dict[packet_id]['count'] == 0:
            data_finish_handler(temp_packet_dict[packet_id]['data'], client_address)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto('OK'.encode('utf-8'), client_address)
'''

def packet_recv_rate():
    with open('recv_rate.txt', 'a') as fp:
        while True:
            global ave_packet_recv_rate
            fp.write(str(datetime.datetime.now()) + '  recv_rate: ' + str(ave_packet_recv_rate)+'\n')
            fp.flush()
            ave_packet_recv_rate = 0
            time.sleep(2)


def start_cmd_server(address):
    cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cmd_socket.bind(address)
    while True:
        data, address = cmd_socket.recvfrom(DATA_SIZE_PER_UDP)
        threading._start_new_thread(cmd_handler, (data, address))


if __name__ == '__main__':
    cmd_server_address = ('127.0.0.1', 35000)
    # data_server_address = ('192.168.46.214', 36000)
    data_server_address = ('192.168.1.100', 36000)
    # start_cmd_server(cmd_server_address)
    start_data_server(data_server_address)
    # data_trans(data_server_address)
