import socket
import threading
import logging.config
from packet import *
import binascii
import hashlib
import time

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')
DATA_SIZE_PER_UDP = 1024


'''
def data_send(data,address):
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
        print(count)
        sock.sendto(send_data, address)
        sock.recvfrom(1024)
    sock.close()
'''

def int2bytes(num, format):
    num_hex_str = hex(num).replace('0x', '')
    format_str = '0' * (format - len(num_hex_str)) + num_hex_str
    return binascii.a2b_hex(format_str)


def send_cmd_packet(data, address):
    if len(data) > DATA_SIZE_PER_UDP:
        return False
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, address)
    reply, remote_addr = sock.recvfrom(1024)
    logger.info(reply.decode('utf-8'))
    sock.close()


def send_data_packet(data, address):
    print('send data packet')
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
        if count==1:
            time.sleep(0.5)
    #send it again
    sent_size = DATA_SIZE_PER_UDP
    point = DATA_SIZE_PER_UDP
    count = 1
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
    gnrs_addr=('192.168.1.100',8899)
    euid = 'ab92b7014f2887ea05450143f4c9ad01'
    query_packet = ICNPacket()
    query_packet.setHeader('bf77ac7196110678d84d03687eab03fb', 'b13ded0762217339428aba5d508ddf5c', '00')
    query_packet.setPayload(binascii.a2b_hex('03' + euid + '00'))
    query_packet.fill_packet()
    query_data = query_packet.grap_packet()

    query_packet.print_packet()
    print(len(query_data))

    while True:
        notify_address=('0.0.0.0',23333)
        notify_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        notify_socket.bind(notify_address)
        notify_data,notify_addr=notify_socket.recvfrom(1024)
        with open('delayflag.txt','w') as fp:
            fp.write(str(time.time()))
            fp.flush()
            fp.close()
        send_cmd_packet(query_data, (gnrs_addr))
        producer_ip = block4ip(euid)
        if not producer_ip == None:
            request_packet = ICNPacket()
            request_packet.setHeader('bf77ac7196110678d84d03687eab03fb', 'b13ded0762217339428aba5d508ddf5c', '00')
            request_packet.setPayload(binascii.a2b_hex('0dab92b7014f2887ea05450143f4c9ad01'))
            request_data = request_packet.grap_packet()
            request_packet.print_packet()
            print(len(request_data))
            send_cmd_packet(request_data, (producer_ip, 35000))
