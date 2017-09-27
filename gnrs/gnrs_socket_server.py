import logging.config
import socket
import threading

from util import dbtool

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


def sign_up_handler(request):
    guid = request.split('###')[1]
    na = request.split('###')[2]
    result = mydb.query('GUID_NA_tbl', {'guid': guid})
    if result == None:
        item = {'guid': guid, 'nas': str([na])}
        mydb.add('GUID_NA_tbl', item)
    else:
        nas_temp = list(eval(result['nas']))
        flag = True
        for i in nas_temp:
            if na == i:
                flag = False
        if flag == True:
            nas_temp.append(na)
            mydb.update('GUID_NA_tbl', {'guid': guid}, {'nas': str(nas_temp)})
    return True


def guid_update(request):
    guid = request.split('###')[1]
    oldna = request.split('###')[2]
    newna = request.split('###')[3]
    result = mydb.query('GUID_NA_tbl', {'guid': guid})
    if result == None:
        item = {'guid': guid, 'nas': str([newna])}
        mydb.add('GUID_NA_tbl', item)
    else:
        nas_temp = list(eval(result['nas']))
        for i in nas_temp:
            if oldna == i:
                nas_temp.remove(i)
        nas_temp.append(newna)
        mydb.update('GUID_NA_tbl', {'guid': guid}, {'nas': str(nas_temp)})
    return 'OK'


def query_handler(request):
    guid = request.split('###')[1]
    result = mydb.query('GUID_NA_tbl', {'guid': guid})
    if not result == None:
        reply = 'OK###' + result['nas']
    else:
        reply = 'NO'
    return reply


def client_handler(client_socket, address):
    request = client_socket.recv(1024).decode("utf-8")

    if request.startswith("SIGNUP###"):
        if sign_up_handler(request) == True:
            reply = 'OK'
        else:
            reply = 'NO'
    elif request.startswith('QUERY###'):
        reply = query_handler(request)
    elif request.startswith('GUIDUPDATE###'):
        reply = guid_update(request)
    else:
        reply = ''
    client_socket.send(reply.encode("utf-8"))
    client_socket.close()
    logger.info("Socket: " + str(address) + " has been closed.")


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((gnrs_ip, gnrs_port))
    logger.info("Server socket bind to " + str(gnrs_ip) + ":" + str(gnrs_port))
    server_socket.listen(5)
    logger.info("Start listening")
    while True:
        logger.info("Waiting for connect...")
        client_socket, address = server_socket.accept()
        logger.info("Connect to client " + str(address))
        threading._start_new_thread(client_handler, (client_socket, address))


if __name__ == '__main__':
    gnrs_ip, gnrs_port = '192.168.46.214', 12700
    db_ip, db_port = '127.0.0.1', 27017

    mydb = dbtool.myDB(db_ip, db_port, 'gnrs')
    # mydb.remove_all('GUID_NA_tbl')
    start_server()
