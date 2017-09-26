import socket
import threading
import logging.config
from packet import *
import binascii

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')
DATA_SIZE_PER_UDP = 1024
temp_packet_dict = []
timeout_dict = []


def cmd_handler(data, address):
    logger.info('Recieve a packet from ' + str(address))
    p = ICNPacket()
    p.gen_from_hex(data)
    p.print_packet()
    reply_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reply_socket.sendto('OK'.encode('utf-8'), address)
    # you can also call another func here


def data_handler(data, address):
    logger.info('UDP packet from: ' + str(address))
    packet_id = binascii.b2a_hex(data[0:20])
    packet_length = int(binascii.b2a_hex(data[20:24]), 16)
    packet_seq = int(binascii.b2a_hex(data[24:26]), 16)
    print(packet_id, ' ', packet_length, ' ', packet_seq)

    packet_dict = {'address': address, 'icn_packet': 3, }

    # you can call your func here


def start_data_server(address):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.bind(address)
    while True:
        data, address = data_socket.recvfrom(DATA_SIZE_PER_UDP + 26)
        threading._start_new_thread(data_handler, (data, address))


def start_cmd_server(address):
    cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cmd_socket.bind(address)
    while True:
        data, address = cmd_socket.recvfrom(DATA_SIZE_PER_UDP)
        threading._start_new_thread(cmd_handler, (data, address))


if __name__ == '__main__':
    cmd_server_address = ('127.0.0.1', 35000)
    data_server_address = ('127.0.0.1', 36000)
    start_cmd_server(cmd_server_address)
    start_data_server(data_server_address)
