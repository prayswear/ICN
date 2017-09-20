import logging.config
import socket

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')
ncs_ip = '127.0.0.1'
ncs_port = 12701

def request_for_reply(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reply = 'EMPTY'
    try:
        sock.connect((ncs_ip, ncs_port))
        logger.info("Connect to server " + ncs_ip + ":" + str(ncs_port))
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


def get_guid(hrn, type):
    request = 'GETGUID###' + hrn + '###' + type
    reply = request_for_reply(request)
    if reply.startswith('OK###'):
        guid = reply.split('###')[1]
        return guid
    else:
        reply = None
    return reply


def query_guid(hrn):
    request = 'QUERYGUID###' + hrn
    reply = request_for_reply(request)
    if reply.startswith('OK###'):
        guid = reply.split('###')[1]
        return guid
    else:
        reply = None
    return reply


def query_hrn(guid):
    request = 'QUERYHRN###' + guid
    reply = request_for_reply(request)
    if reply.startswith('OK###'):
        hrn = reply.split('###')[1]
        return hrn
    else:
        reply = None
    return reply


def query_type(guid):
    request = 'QUERYTYPE###' + guid
    reply = request_for_reply(request)
    if reply.startswith('OK###'):
        type = reply.split('###')[1]
        return type
    else:
        reply = None
    return reply

def query_all():
    request='QUERYALL###'
    reply=request_for_reply(request)
    guid_list=[]
    if reply.startswith('OK###'):
        result=reply.split('###')[1]
        guid_list=list(eval(result))
    return guid_list



if __name__ == '__main__':
    ncs_ip = '127.0.0.1'
    ncs_port = 12701

    list=query_all()
    print(list)

    # print(get_guid('lijqphone', 'phone'))
    # temp = query_guid('lijqphone')
    # print(temp)
    # print(query_hrn(temp))
    # print(query_type(temp))
    #
    # print(get_guid('lijqphone', 'phone'))
    # print(query_type('123'))
    # print(query_hrn('123'))
    # print(query_guid('123'))
