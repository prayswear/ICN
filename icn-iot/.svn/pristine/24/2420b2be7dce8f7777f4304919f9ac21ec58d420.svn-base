import time
import os
import urllib.request
import urllib.parse


def sseenndd(fpfp,idid1,idid2):
    params = urllib.parse.urlencode({'filePath': fpfp, 'euid': idid1, 'na': idid2})
    url = "http://127.0.0.1:8081/icn-api/v1/monitor/notify?%s" % params
    urllib.request.urlopen(url)
    # with urllib.request.urlopen(url) as f:
    #     print(f.read().decode('utf-8'))

sseenndd('http://192.168.150.240/thisismp4.mp4','0dab92b7014f2887ea05450143f4c9ad01',str(address[0]))