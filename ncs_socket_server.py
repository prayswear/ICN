import socket
import threading
import logging.config
import dbtool
import signature

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


def get_guid(request):
    # request is like GETGUID###hrn###type
    hrn = request.split('###')[1]
    type = request.split('###')[2]
    guid = signature.gen_guid(hrn)
    result = mydb.query('NCS_tbl', {'hrn': hrn})
    if result == None:
        item = {'guid': guid, 'hrn': hrn, 'type': type}
        mydb.add('NCS_tbl', item)
        reply = 'OK###' + guid
    else:
        reply = 'NO'
    return reply


def query_hrn(request):
    # request is like QUERYHRN###guid
    guid = request.split('###')[1]
    result = mydb.query('NCS_tbl', {'guid': guid})
    if not result == None:
        reply = 'OK###' + result['hrn']
    else:
        reply = 'NO'
    return reply


def query_guid(request):
    # request is like QUERYGUID###hrn
    hrn = request.split('###')[1]
    result = mydb.query('NCS_tbl', {'hrn': hrn})
    if not result == None:
        reply = 'OK###' + result['guid']
    else:
        reply = 'NO'
    return reply

def query_all(request):
    result=mydb.query_all('NCS_tbl',{})
    if result==None:
        return 'NO'
    guid_list = []
    for i in result:
        guid_list.append(i['guid'])
    reply='OK###'+str(guid_list)
    return reply




def query_type(request):
    # request is like QUERYtype###guid
    guid = request.split('###')[1]
    result = mydb.query('NCS_tbl', {'guid': guid})
    if not result == None:
        reply = 'OK###' + result['type']
    else:
        reply = 'NO'
    return reply


def client_handler(client_socket, address):
    request = client_socket.recv(1024).decode('utf-8')

    if request.startswith('GETGUID###'):
        reply = get_guid(request)
    elif request.startswith('QUERYHRN###'):
        reply = query_hrn(request)
    elif request.startswith('QUERYGUID###'):
        reply = query_guid(request)
    elif request.startswith('QUERYTYPE###'):
        reply = query_type(request)
    elif request.startswith('QUERYALL###'):
        reply=query_all(request)
    else:
        reply = 'NO'
    client_socket.send(reply.encode('utf-8'))
    client_socket.close()
    logger.info("Socket: " + str(address) + " has been closed.")


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ncs_ip, ncs_port))
    logger.info("Server socket bind to " + str(ncs_ip) + ":" + str(ncs_port))
    server_socket.listen(5)
    logger.info("Start listening")
    while True:
        logger.info("Waiting for connect...")
        client_socket, address = server_socket.accept()
        logger.info("Connect to client " + str(address))
        threading._start_new_thread(client_handler, (client_socket, address))


if __name__ == '__main__':
    ncs_ip, ncs_port = '127.0.0.1', 12701
    db_ip, db_port = '127.0.0.1', 27017
    mydb = dbtool.myDB(db_ip, db_port, 'ncs')
    # print(query_all('QUERYALL###'))
    # mydb.remove_all('GUID_NA_tbl')
    start_server()
