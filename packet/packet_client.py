import logging.config
import socket

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')
BUFFER_SIZE = 1024


def send_packet(packet):
    packet_size = len(packet)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((packet_server_ip, packet_server_port))
        logger.info("Connect to server " + packet_server_ip + ":" + str(packet_server_port))
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


if __name__ == '__main__':
    packet_server_ip = '127.0.0.1'
    packet_server_port = 35000
    data = b'\x01#Eg\x89\xab\xcd\xef\x01#Eg\x89\xab\xcd\xef\x12\xab\xcd\xef\xaf\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfa\x87eC!\x124Vx\xee7%\x16\xab\xcd\xef\xdc\xba'
    print(len(data))
    send_packet(data)
