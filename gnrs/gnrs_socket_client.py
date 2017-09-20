import logging.config
import socket

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')

def request_for_reply(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reply = 'EMPTY'
    try:
        sock.connect((gnrs_ip, gnrs_port))
        logger.info("Connect to server " + gnrs_ip + ":" + str(gnrs_port))
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


def sign_up(guid, na):
    request = 'SIGNUP###' + guid + '###' + na
    reply = request_for_reply(request)
    if reply.startswith('OK'):
        return True
    else:
        return False

def guid_update(guid,oldna,newna):
    request='GUIDUPDATE###'+guid+'###'+oldna+'###'+newna
    reply=request_for_reply(request)
    if reply.startswith('OK'):
        return True
    else:
        return False



def query(guid):
    request = 'QUERY###' + guid
    reply = request_for_reply(request)
    if reply.startswith('OK'):
        nas = reply.split('###')[1]
        result = list(eval(nas))
        return result
    else:
        return None


if __name__ == '__main__':
    gnrs_ip = '127.0.0.1'
    gnrs_port = 12700
    print(query('111'))
    print(sign_up('123','1.1.1.1'))
    print(sign_up('123','1.1.1.1'))
    print(query('123'))
    print(sign_up('123','2.2.2.2'))
    print(query('123'))


