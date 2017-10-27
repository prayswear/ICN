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
UDP_MTU = STD_UDP_MTU
ICN_MTU = UDP_MTU - 36  # 36 is len of none-tlv icn head
ICN_TEMP_MTU = ICN_MTU - 8  # 8 is len of tlv
ICN_CONTENT_MTU = ICN_TEMP_MTU - 1 - 16  # 1 is icn type, 16 is content euid
icn_data_reply_type = '09'

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
            time.sleep(3)


def data_finish_handler(packet_id, address):
    logger.info('Recieve a packet from ' + str(address))
    p = ICNPacket()
    data_hex = temp_packet_dict[packet_id]['data']
    p.gen_from_hex(data_hex)
    p.print_packet_without_payload()
    content_euid = binascii.b2a_hex(p.payload[1:17])
    timestamp=binascii.b2a_hex(p.payload[17:21]).decode('utf-8')+'_'+str(int(time.time()))
    real_data = p.payload[21:]
    # reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # reply_socket.sendto('OK'.encode('utf-8'), address)
    if content_euid.decode('utf-8')=='ab92b7014f2887ea05450143f4c9ad01':
        with open('cam1_'+timestamp+'.h264', 'wb') as f:
            f.write(real_data)
            f.close()
        os.system('avconv -r 24 -i cam1_'+timestamp+'.h264 -vcodec copy cam1_' + timestamp + '.mp4 -y')
        os.system('cp cam1_'+timestamp+'''.mp4 /home/lijq/Desktop/apache-tomcat-7.0.82/webapps/page/cam1_''' + timestamp + '''.mp4''')
        os.system('rm cam1_'+timestamp+'.h264')
        # filepath = 'file:///home/lijq/PycharmProjects/ICN/packet/cam1_' + filetime + '.mp4'
        filepath = 'cam1_' + timestamp + '.mp4'
        # with open('input'+timestamp+'.txt', 'wb') as f:
        #     f.write(timestamp.encode('utf-8'))
        #     f.close()
        notify_page(filepath, content_euid, str(address[0]))
    else:
        print(content_euid)
        with open('temprature_'+content_euid.decode('utf-8')+'.txt', 'wb') as f:
            f.write(real_data)
            f.close()


def timeout_handler(packet_id, address):
    start_time = time.time()
    while True:
        timegap = time.time() - start_time
        if timegap > 6:
            if packet_id in temp_packet_dict.keys():
                data_finish_handler(packet_id, address)
                global ave_packet_recv_rate
                total = temp_packet_dict[packet_id]['total']
                ave_packet_recv_rate = (total - temp_packet_dict[packet_id]['count']) / total
                del temp_packet_dict[packet_id]
            break


def data_handler(data, address):
    # logger.info('Recv UDP packet from: ' + str(address))
    recv_times = 1
    p = ICNPacket()
    p.gen_from_hex(data)
    packet_id = binascii.b2a_hex(p.tlv[0:2])
    packet_length = int(binascii.b2a_hex(p.tlv[2:6]), 16)
    packet_seq = int(binascii.b2a_hex(p.tlv[6:8]), 16)
    DATA_SIZE_PER_UDP = ICN_CONTENT_MTU
    num = packet_length / DATA_SIZE_PER_UDP
    if num == int(num):
        packet_num = int(num) * recv_times - recv_times + 1
    else:
        packet_num = (int(num) + 1) * recv_times - recv_times + 1
    logger.info(packet_id.decode('utf-8')+' '+ str(packet_length)+ ' '+ str(packet_num)+' '+str(packet_seq))
    real_data = p.payload[17:len(p.payload)]
    if packet_seq == 0:
        temp_dict = {}
        temp_data = binascii.a2b_hex('00' * packet_length)
        temp_dict['data'] = real_data + temp_data[len(real_data):packet_length]
        temp_dict['count'] = packet_num
        temp_dict['total'] = temp_dict['count']
        temp_packet_dict[packet_id] = temp_dict
        logger.info('packet_seq: ' + str(packet_seq))
        threading._start_new_thread(timeout_handler, (packet_id, address))
    else:
        if not packet_id in temp_packet_dict.keys():
            return
        else:
            temp_data = temp_packet_dict[packet_id]['data'][0:packet_seq * DATA_SIZE_PER_UDP] + real_data + \
                        temp_packet_dict[packet_id]['data'][
                        packet_seq * DATA_SIZE_PER_UDP + len(real_data):packet_length]
            temp_packet_dict[packet_id]['data'] = temp_data
            logger.info('packet_seq: ' + str(packet_seq))
    temp_packet_dict[packet_id]['count'] -= 1
    logger.info('count: ' + str(temp_packet_dict[packet_id]['count']))
    if temp_packet_dict[packet_id]['count'] == 0:
        global ave_packet_recv_rate
        ave_packet_recv_rate = 1
        data_finish_handler(packet_id, address)
        del temp_packet_dict[packet_id]


def start_data_server(address):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.bind(address)
    logger.info('start data server')
    threading._start_new_thread(packet_recv_rate, ())
    while True:
        data, client_address = data_socket.recvfrom(UDP_MTU)
        # print('get new udp packet from: '+str(client_address))
        threading._start_new_thread(data_handler, (data, client_address))


def cmd_handler(data, address):
    logger.info('Recieve a packet from ' + str(address))
    p = ICNPacket()
    p.gen_from_hex(data)
    p.print_packet()
    reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reply_socket.sendto('OK'.encode('utf-8'), address)


def start_cmd_server(address):
    cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cmd_socket.bind(address)
    while True:
        data, address = cmd_socket.recvfrom(UDP_MTU)
        threading._start_new_thread(cmd_handler, (data, address))


if __name__ == '__main__':
    cmd_address = ('0.0.0.0', 35000)
    data_address = ('0.0.0.0', 36000)
    start_data_server(data_address)
    # start_cmd_server(cmd_address)
