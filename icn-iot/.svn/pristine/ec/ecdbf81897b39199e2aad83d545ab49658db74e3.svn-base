#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import subprocess
from time import sleep 
import logging.config
from socket import *
import binascii
import json
import re

def search(pattern,text,flag):    
    #print(text)
    m=re.search(pattern,text)
    if m is not None:
       return m.group(flag)

def get_ip(cmd):
   ip_cur = '0.0.0.0'
   while ip_cur == '0.0.0.0':
        obj = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        obj.wait()
        lines = obj.stdout.readlines()                        
        for eachline in lines:
            eachline= eachline.decode('gbk')
            #print(eachline)
            strs='IPv4 地址'
            if strs in eachline:               
               content=search('IPv4 地址 . . . . . . . . . . . . :(.*?)\r\n',eachline,1)
               #print(content)
               ip_cur = str(content)
               print(ip_cur)
               break        
   return ip_cur

def send_data_request(S_EUID,D_EUID,C_EUID,NA,port):
    address = (NA, port)
    s = socket(AF_INET,SOCK_DGRAM)    
    flag=1
    while flag:        
        s_EUID=binascii.a2b_hex(S_EUID)        
        d_EUID=binascii.a2b_hex(D_EUID)
        sev_type=binascii.a2b_hex(hex(22).replace('0x',''))
        Head_len=binascii.a2b_hex(hex(36).replace('0x',''))
        ICN_check=binascii.a2b_hex(hex(4444).replace('0x',''))
        packet_type=binascii.a2b_hex('0'+hex(1).replace('0x',''))      
        c_EUID=binascii.a2b_hex(C_EUID)            
        data=s_EUID+d_EUID+ sev_type+Head_len\
        +ICN_check+packet_type+c_EUID
        print(len(data))
        if not data:  
           break  
        s.sendto(data,address)
        flag=0  
    s.close()
    

def ip_cmp(cmd,S_EUID,D_EUID,C_EUID,NA,port,IP_cur,get_cnt):    
    ip_next=get_ip(cmd)
    get_cnt=get_cnt+1
    if time_flag:
        if ip_cur!='0.0.0.0' and ip_next !='0.0.0.0':
            if ip_cur == ip_next:
                change_flag=0
                print('change_flag='+str(change_flag))
            else:
                change_flag=1
                print('change_flag='+str(change_flag))                
                send_data_request(S_EUID,D_EUID,C_EUID,NA,port)
    return ip_next



if __name__ == '__main__':
    
    cmd='ipconfig'
    
    get_cnt=0 #ip 获取次数计数器
    T_interval=0.1 #ip 获取周期
    ip_cur='0.0.0.0'    
    ip_next='0.0.0.0'
    ip_cur=get_ip(cmd)
    #ip_cur='192.168.110.1'
    get_cnt=get_cnt+1
    
    time_flag=1
    
    S_EUID='aaaa'
    D_EUID='bbbb'
    C_EUID='cccc'
    NA='192.168.1.100' 
    port=35000

    while time_flag:
       ip_next=ip_cmp(cmd,S_EUID,D_EUID,C_EUID,NA,port,ip_cur,get_cnt)
       print('IP_next='+ip_next)
       sleep(T_interval)
       ip_cur=ip_next
       print('IP_cur='+ip_next)
       
    
    
    

            
            
            
                
            
    


