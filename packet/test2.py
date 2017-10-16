from packet import *
import binascii
import logging.config
import time

with open('delayflag.txt', 'w') as fp:
    fp.write(str(time.time()))
    fp.flush()
    fp.close()

with open('delayflag.txt','r') as f:
    a=float(f.readline())
    print(a)
