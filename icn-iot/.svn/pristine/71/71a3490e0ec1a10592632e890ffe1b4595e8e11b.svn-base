#-*- coding:utf-8 -*-
import io

import logging
import socketserver
from threading import Condition
from http import server
import time
import hashlib
import os
import RPi.GPIO as GPIO
from udp_gnrs import *

from ncs_socket_client import *
from gnrs_socket_client import *

from wifidetect import *
import logging.config

def getth():
    channel =4
    data = []
    j = 0
    GPIO.setmode(GPIO.BCM)
    time.sleep(0.05)
    GPIO.setup(channel, GPIO.OUT)
    GPIO.output(channel, GPIO.LOW)
    time.sleep(0.02)
    GPIO.output(channel, GPIO.HIGH)
    GPIO.setup(channel, GPIO.IN)
    while GPIO.input(channel) == GPIO.LOW:
        continue
    while GPIO.input(channel) == GPIO.HIGH:
        continue
    while j < 40:
        k = 0
        while GPIO.input(channel) == GPIO.LOW:
            continue
        while GPIO.input(channel) == GPIO.HIGH:
            k += 1
            if k > 100:
                break
        if k < 8:
            data.append(0)
        else:
            data.append(1)
        j += 1
    humidity_bit = data[0:8]
    humidity_point_bit = data[8:16]
    temperature_bit = data[16:24]
    temperature_point_bit = data[24:32]
    check_bit = data[32:40]
    humidity = 0
    humidity_point = 0
    temperature = 0
    temperature_point = 0
    check = 0
    for i in range(8):
        humidity += humidity_bit[i] * 2 ** (7-i)
        humidity_point += humidity_point_bit[i] * 2 ** (7-i)
        temperature += temperature_bit[i] * 2 ** (7-i)
        temperature_point += temperature_point_bit[i] * 2 ** (7-i)
        check += check_bit[i] * 2 ** (7-i)
    tmp = humidity + humidity_point + temperature + temperature_point
    GPIO.cleanup()
    if check == tmp:
        return [temperature, humidity]
    else:
        return [temperature, humidity]
PAGE="""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>杨骏的工位监控</title>
</head>
<body>
    <h1>杨骏的工位监控</h1>
    <img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')

#mytable = {0: 'HRN_GUID_tbl', 1: 'GUID_NA_tbl', 2: 'LUID_GUID_tbl'}
mytable = {0: 'HRN_GUID_tbl'}
db_ip, db_port = '127.0.0.1', 27017
db_name = 'GWmapping'
dbbbbbb = dbtool.myDB(db_ip, db_port, db_name)

username = 'admin'





while 1:
    # filename_camera = 'camera1 '+str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    data1 = getth()
    ttt = str(time.strftime("%Y-%m-%d-%H-%M", time.localtime()))
    filename_th1 = 'th'+ttt
    # th1_fp = open('file/'+str(filename_th1)+'_tmp','a')
    th1_fp = open('file/'+str(filename_th1),'w')
    # filename_th2 = 'th2'
    # th2_fp = open('file/'+str(filename_th2)+'_tmp','a')
    th1_fp.write(str(data1[0])+' '+str(data1[1]))
    # th2_fp.write(str(time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()))+str(data1[1])+'\n')
    th1_fp.close()
    # th2_fp.close()


    nnccssresult1 = query_guid(str(filename_th1))
    # nnccssresult2 = query_guid(str(filename_th2))
    #nnccssresult = nccar_getguid(str(filename_camera)+'.h264')



    if nnccssresult1 == None:
        ncs_th1 = get_guid(str(filename_th1),'file')[0:32]
    else:
        ncs_th1 = nnccssresult2

    # if nnccssresult2 == None:
    #     ncs_th2 = get_guid(str(filename_th2),'file')[0:32]
    # else:
    #     ncs_th2 = nnccssresult2

    #sign_reply_camera = sign_up(str(ncs_camera), get_ip())
    # print('------------------1')
    sign_reply_th1 = udp_gnrs_reg(str(ncs_th1), get_ip())
    # print('------------------2')
    # sign_reply_th2 = udp_gnrs_reg(str(ncs_th2), get_ip())

    # print('------------------3')

    if sign_reply_th1==True:
        result1 = dbbbbbb.query(mytable[0], {'guid': str(ncs_th1)})
        if result1 == None:
            dbbbbbb.add(mytable[0], {'guid': str(ncs_th1), 'hrn': str(filename_th1)})
        else:
            dbbbbbb.update(mytable[0], {'guid': str(ncs_th1)},{'hrn': str(filename_th1)})



    # if sign_reply_th2==True:
    #     result1 = dbbbbbb.query(mytable[0], {'guid': str(ncs_th2)})
    #     if result1 == None:
    #         dbbbbbb.add(mytable[0], {'guid': str(ncs_th2), 'hrn': str(filename_th2)})
    #     else:
    #         dbbbbbb.update(mytable[0], {'guid': str(ncs_th2)},{'hrn': str(filename_th2)})



    #     dbbbbbb.add(mytable[0], {'hrn': str(filename_camera)+'.h264', 'luid': str(ncs_camera)[0:16]})
    #     dbbbbbb.add(mytable[1], {'guid': str(ncs_camera), 'na': get_ip()})
    #     dbbbbbb.add(mytable[2], {'luid': str(ncs_camera)[0:16], 'guid': str(ncs_camera)})
###########################################
    # filename_th = 'th1 '+str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # fp=open('file/'+str(filename_th)+'.th','w')
    # fp.write(str(getth()))
    # fp.close()
    # ncs_th = get_guid(str(filename_th)+'.th', get_ip())[0:32]
    # sign_reply_th = sign_up(str(ncs_th), get_ip())

    # if sign_reply_th==True:
    #     result2 = dbbbbbb.query(mytable[0], {'guid': str(ncs_th)})
    #     if result2 == None:
    #         dbbbbbb.add(mytable[0], {'guid': str(ncs_th), 'hrn': str(filename_th)+'.h264'})
    #     else:
    #         dbbbbbb.update(mytable[0], {'guid': str(ncs_th)},{'hrn': str(filename_th)+'.h264'})


        # dbbbbbb.add(mytable[0], {'hrn': str(filename_th)+'.th', 'luid': str(ncs_th)[0:16]})
    #     dbbbbbb.add(mytable[1], {'guid': str(ncs_th), 'na': get_ip()})
    #     dbbbbbb.add(mytable[2], {'luid': str(ncs_th)[0:16], 'guid': str(ncs_th)})
##########################################

    # print(sign_reply_th)

    time.sleep(60)

    # os.system('cp file/th1_tmp file/th1')
    # os.system('cp file/th2_tmp file/th2')
    # print('saved as  '+str(filename_camera)+'.h264')
    # print('saved as  '+str(filename_th)+'.th')
