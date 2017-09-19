import logging.config
import socket

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


def request_for_reply(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reply = 'EMPTY'
    try:
        sock.connect((test_ip, test_port))
        logger.info("Connect to server " + test_ip + ":" + str(test_port))
        sock.send(request.encode("utf-8"))
        logger.info("Request: " + request + " has been sent.")
        reply = sock.recv(1024).decode("utf-8")
        logger.info("Reply is: " + reply)
    except socket.error as e:
        logger.error(e)
    finally:
        sockname = sock.getsockname()
        sock.close()
        logger.info('Socket: ' + str(sockname) + ' has been closed.')
    return reply



if __name__ == '__main__':
    test_ip = '127.0.0.1'
    test_port = 12700
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bsize = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    print(bsize)
    data='a'*40000
    print(len(data))
    reply=request_for_reply(data)

