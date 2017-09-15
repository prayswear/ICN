import socket
import threading
import logging.config
import dbtool
import signature
import datetime

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


def sign_up_handler(request):
    guid = request.split('###')[1]
    na = request.split('###')[2]
    nas = mydb.query('GUID_NA_tbl', {'guid': guid})
    if nas == None:
        item = {'guid': guid, 'nas': str([na])}
        mydb.add('GUID_NA_tbl', item)
    else:
        nas_temp = list(eval(nas['nas']))
        flag = True
        for i in nas_temp:
            if na == i:
                flag = False
        if flag == True:
            nas_temp.append(na)
            mydb.update('GUID_NA_tbl', {'guid': guid}, {'nas': str(nas_temp)})
    return True


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
    gnrs_ip, gnrs_port = '127.0.0.1', 12700
    db_ip, db_port = '127.0.0.1', 27017

    mydb = dbtool.myDB(db_ip, db_port, 'gnrs')
    # mydb.remove_all('GUID_NA_tbl')
    start_server()
