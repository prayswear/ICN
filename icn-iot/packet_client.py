import logging.config
import socket
from packet import *
import binascii

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')
BUFFER_SIZE = 1024


def send_packet(dst_ip, dsp_port, packet):
    packet_size = len(packet)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((dst_ip, dsp_port))
        logger.info("Connect to server " + dst_ip + ":" + str(dsp_port))
        sock.send(str(packet_size).encode("utf-8"))
        logger.info("Request: " + str(packet_size) + " has been sent.")
        reply = sock.recv(BUFFER_SIZE).decode("utf-8")
        logger.info("Reply is: " + reply)
        sent_size = 0
        point = 0
        while sent_size < packet_size:
            remained_size = packet_size - sent_size
            send_size = BUFFER_SIZE if remained_size > BUFFER_SIZE else remained_size
            send_data = packet[point:point + send_size]
            sent_size += send_size
            sock.send(send_data)
        logger.info('over')
    except socket.error as e:
        logger.error(e)
    finally:
        sockname = sock.getsockname()
        sock.close()
        logger.info('Socket: ' + str(sockname) + ' has been closed.')


def lanjun_func(src_guid, dst_guid, src_na, dst_na, service_type, payload):
    packet = ICNPacket()
    packet.setHeader(src_guid, dst_guid, src_na, dst_na, service_type)
    packet.setPayload(payload)
    packet.fill_packet()
    data = packet.grap_packet()
    return data


if __name__ == '__main__':
    print(binascii.a2b_hex('ee'))
    print(binascii.a2b_hex(b'ee'))
    packet_server_ip = '127.0.0.1'
    packet_server_port = 35000
    # data = b'\x01#Eg\x89\xab\xcd\xef\x01#Eg\x89\xab\xcd\xef\x12\xab\xcd\xef\xaf\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfa\x87eC!\x124Vx\xee7%\x16\xab\xcd\xef\xdc\xba'
    packet = ICNPacket()
    packet.setHeader('0123456789abcdef0123456789abcdef12abcdef', 'affffffffffffffffffffffffffffffffffffffa', '87654321',
                     '12345678', '11')
    packet.setPayload(binascii.a2b_hex('e' * 346536))
    print(packet.payload)
    packet.fill_packet()
    data = packet.grap_packet()
    packet.print_packet()
    print(len(data))
    send_packet(packet_server_ip, packet_server_port, data)
