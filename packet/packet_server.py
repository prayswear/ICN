import socket
import threading
import logging.config
from packet import *

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')
BUFFER_SIZE = 1024


def client_handler(client_socket, address):
    packet_size = int(client_socket.recv(BUFFER_SIZE).decode("utf-8"))
    print(packet_size)
    client_socket.send('OK'.encode("utf-8"))
    recved_size = 0
    recv_packet = b''
    while recved_size < packet_size:
        remained_size = packet_size - recved_size
        recv_size = BUFFER_SIZE if remained_size > BUFFER_SIZE else remained_size
        recv_data = client_socket.recv(recv_size)
        recved_size += recv_size
        recv_packet += recv_data
    print(recv_packet)
    a=ICNPacket()
    a.gen_from_hex(recv_data)
    a.print_packet()
    client_socket.close()
    logger.info("Socket: " + str(address) + " has been closed.")


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((packet_server_ip, packet_server_port))
    logger.info("Server socket bind to " + str(packet_server_ip) + ":" + str(packet_server_port))
    server_socket.listen(5)
    logger.info("Start listening")
    while True:
        logger.info("Waiting for connect...")
        client_socket, address = server_socket.accept()
        logger.info("Connect to client " + str(address))
        threading._start_new_thread(client_handler, (client_socket, address))


if __name__ == '__main__':
    packet_server_ip, packet_server_port = '127.0.0.1', 35000
    start_server()
