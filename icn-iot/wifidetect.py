#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import subprocess
from time import sleep
from ncs_socket_client import *
# from gnrs_socket_client import *
import pymongo
import logging.config
import dbtool
from udp_gnrs import *

mac_list = ["88:10:36:30:41:5e","54:36:9b:31:a7:7f","88:10:36:30:30:f1","88:10:36:30:41:61","88:10:36:30:40:ec"]
ip_list = ['192.168.4.100','192.168.5.100','192.168.10.100','192.168.2.100','192.168.3.100']
state = [0,0,0,0,0]
state_old = [0,0,0,0,0]
cmd = 'iw dev wlan0 station dump | grep Station'


def sendonline(mymac,myip):
    import socket
    import time
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.1.252', 1122))
    data = 'I am online! AP '+mymac+' NA is '+myip
    print('Send:'+ data)
    sock.send(data.encode("utf-8"))
    sock.close()

def get_ip():
    iipp = '0.0.0.0'
    while iipp == '0.0.0.0':
        obj = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        obj.wait()
        sizeofmac_list = len(mac_list)
        lines = obj.stdout.readlines()
        for i in range(sizeofmac_list):
            for strs in lines:
                if str(strs).find(mac_list[i]) > 0:
                    iipp = ip_list[i]
                    break
        sleep(0.1)
    return iipp




if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('myLogger')

    mytable = {0: 'HRN_GUID_tbl'}
    db_ip, db_port = '127.0.0.1', 27017
    db_name = 'GWmapping'
    ddddddb = dbtool.myDB(db_ip, db_port, db_name)

    username = 'admin'



    lastna = 'None'
    nowna = 'None'
    while True:
        obj = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        obj.wait()
        sizeofmac_list = len(mac_list)
        for i in range(sizeofmac_list):
            state_old[i] = state[i]
        lines = obj.stdout.readlines()
        state = [0,0,0,0,0]
        for i in range(sizeofmac_list):
            for strs in lines:
                if str(strs).find(mac_list[i]) > 0:
                    state[i] = 1
                    break
    #    for i in range(3):
    #        print ("%d -> %d" % (state_old[i],state[i]))
        result1 = ddddddb.query_all(mytable[0], {})
        for i in range(sizeofmac_list):
            if state[i] > state_old[i]:
                lastna = nowna
                nowna = ip_list[i]
                print("------%s->%s-------" % (lastna,nowna))
                print("AP %d - %s Linked! NA is %s" % (i,mac_list[i],ip_list[i]))
                #sendonline(mac_list[i],ip_list[i])




                udp_gnrs_reg('2613f2a93a0683bdc6260edfcfec6d76',nowna)
                for i1 in result1:
                    logger.info(i1)

                    if lastna!='None':
                        print("--------REG %s NA:%s->%s"%(str(i1["guid"]),lastna,nowna))
                        udp_gnrs_reg(str(i1["guid"]),nowna)
                        #guid_update(str(i1["guid"]),lastna,nowna)


        time.sleep(0.1)