import socket
import threading
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


def client_handler(client_socket, address):
    request = client_socket.recv(62780).decode("utf-8")
    print(len(request))
    reply='ok'
    client_socket.send(reply.encode("utf-8"))
    client_socket.close()
    logger.info("Socket: " + str(address) + " has been closed.")


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((test_ip, test_port))
    logger.info("Server socket bind to " + str(test_ip) + ":" + str(test_port))
    server_socket.listen(5)
    logger.info("Start listening")
    while True:
        logger.info("Waiting for connect...")
        client_socket, address = server_socket.accept()
        logger.info("Connect to client " + str(address))
        threading._start_new_thread(client_handler, (client_socket, address))


if __name__ == '__main__':
    test_ip, test_port = '127.0.0.1', 12700
    start_server()
