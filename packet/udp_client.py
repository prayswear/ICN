import socket
import threading
import logging.config
from packet import *
import binascii
import hashlib

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')
DATA_SIZE_PER_UDP = 1024


def int2bytes(num, format):
    num_hex_str = hex(num).replace('0x', '')
    format_str = '0' * (format - len(num_hex_str)) + num_hex_str
    return binascii.a2b_hex(format_str)

def send_cmd_packet(address,data):
    if len(data)>DATA_SIZE_PER_UDP:
        return False
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, address)
    reply,remote_addr=sock.recvfrom(1024)
    logger.info(reply.decode('utf-8'))
    sock.close()

def send_data_packet(address, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_size = len(data)
    sent_size = 0
    point = 0
    count = 0
    id = binascii.a2b_hex(hashlib.sha1(data).hexdigest()[0:4])
    print(id)
    while sent_size < packet_size:
        remained_size = packet_size - sent_size
        send_size = DATA_SIZE_PER_UDP if remained_size > DATA_SIZE_PER_UDP else remained_size
        send_data = id + int2bytes(packet_size, 8) + int2bytes(count, 4)
        send_data += data[point:point + send_size]
        point += send_size
        sent_size += send_size
        count += 1
        sock.sendto(send_data, address)
    sock.close()


if __name__ == '__main__':
    cmd_server_address = ('127.0.0.1', 35000)
    data_server_address = ('127.0.0.1', 36000)
    packet = ICNPacket()
    packet.setHeader('0123456789abcdef0123456789abcdef', 'afffffffffffffffffffffffffffffff', '00')
    packet.setPayload(binascii.a2b_hex('ee' * 100))
    packet.fill_packet()
    data = packet.grap_packet()
    packet.print_packet()
    print(len(data))
    send_cmd_packet(cmd_server_address,data)
    # send_data_packet(udp_server_address, data)
