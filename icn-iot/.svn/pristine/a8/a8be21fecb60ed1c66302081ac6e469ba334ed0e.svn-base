import socket
import threading
import logging.config
from packet import *
import binascii
import time
from send_client import *
from ncs_socket_client import *
import dbtool
import os

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')
DATA_SIZE_PER_UDP = 1024
temp_packet_dict = {}

def writerip(iipp):
    x=open('rip','w')
    x.write(iipp)
    x.close()
def getrip():
    x=open('rip','r')
    return x.read()
    x.close()

def cmd_handler(data, address):
    logger.info('Recieve a packet from ' + str(address))
    p = ICNPacket()
    p.gen_from_hex(data)
    # p.print_packet()
    reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reply_socket.sendto('OK'.encode('utf-8'), address)
    xxx = p.payload
    yyy = binascii.b2a_hex(xxx).decode('utf-8')
    gguuiidd = yyy[2:34]
    print('-----'+yyy+'*****')
    sendguidfile(address[0],gguuiidd)
    writerip(address[0])

def sendguidfile(ipip,gguuiidd):
    nnaammee = getfn(gguuiidd)
    os.system('cp file/'+nnaammee+' file/nya -rf')
    #x = open('file/'+nnaammee,'rb')
    x = open('file/nya','r')
    p = ICNPacket()
    aaa = x.read()
    p.setHeader('b498dce7ea1f7a1a1b11a48dfef58303', '7ee30ed78da46257a17047254b7d6a4b', '00')
    p.setPayload(binascii.a2b_hex('09'+gguuiidd)+aaa.encode('utf-8'))
    p.fill_packet()
    print(aaa)
    # p.print_packet()
    data = p.grap_packet()
    send_data_packet(p, (ipip,36000))





def getfn(guid):
    print('############'+guid+"#################")
    db_ip, db_port = '127.0.0.1', 27017
    mydb = dbtool.myDB(db_ip, db_port, 'GWmapping')
    rs=mydb.query('HRN_GUID_tbl',{'guid':guid})
    return rs['hrn']



def data_finish_handler(data, address):
    logger.info('Recieve a packet from ' + str(address))
    p = ICNPacket()
    p.gen_from_hex(data)
    p.print_packet()
    reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reply_socket.sendto('OK'.encode('utf-8'), address)


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
        temp_dict['time'] = time.time()
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
    timegap = time.time() - temp_packet_dict[packet_id]['time']
    if temp_packet_dict[packet_id]['count'] == 0 or timegap > 2:
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


# you can call your func here


def start_data_server(address):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.bind(address)
    print('start data server')
    while True:
        data, address = data_socket.recvfrom(DATA_SIZE_PER_UDP + 26)
        threading._start_new_thread(data_handler2, (data, address))


def start_cmd_server(address):
    cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cmd_socket.bind(address)
    while True:
        data, address = cmd_socket.recvfrom(DATA_SIZE_PER_UDP)
        threading._start_new_thread(cmd_handler, (data, address))


if __name__ == '__main__':
    cmd_server_address = ('0.0.0.0', 35000)
    data_server_address = ('0.0.0.0', 36000)
    start_cmd_server(cmd_server_address)
    #start_data_server(data_server_address)
