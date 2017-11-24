#!/usr/bin/env python
# -*- coding: utf-8 -*-
import iwlist
import time
import os




def getdb():
    wifiscan = iwlist.scan(interface='wlan0')
    wifilist = iwlist.parse(wifiscan)
    dblist = [-1000,0,0]
    for i in wifilist:
        if "5G" in i["essid"]:
            # if i["essid"] == "5G-10":
            #     dblist[0] = int(i["signal_level_dBm"])
            if i["essid"] == "5G-2":
                dblist[1] = int(i["signal_level_dBm"])
            if i["essid"] == "5G-3":
                dblist[2] = int(i["signal_level_dBm"])
    return dblist

def changewifi(x):
    # if x == 0:
    #     os.system('''wpa_cli -i wlan0 select_network 0''')
    if x == 1:
        os.system('''wpa_cli -i wlan0 select_network 1''')
        os.system('''ifconfig wlan0 192.168.2.234 netmask 255.255.255.0''')
        os.system('''route add default gw 192.168.2.1''')
        os.system('''route add -net 192.168.1.0/24 gw 192.168.1.1''')
    if x == 2:
        os.system('''wpa_cli -i wlan0 select_network 2''')
        os.system('''ifconfig wlan0 192.168.3.234 netmask 255.255.255.0''')
        os.system('''route add default gw 192.168.3.1''')
        os.system('''route add -net 192.168.1.0/24 gw 192.168.1.1''')

if __name__ == '__main__':
    changewifi(1)
    nnn = 2
    print('--------INIT to 5G-2--------')
    while True:
        dblist = getdb()
        print(dblist)
        print('Now: '+str(nnn))
        if (dblist[2] - dblist[1] > 10)and nnn != 3:
            print("5G-2 -> 5G-3")
            changewifi(2)
            nnn = 3
        if (dblist[1] - dblist[2] > 10)and nnn != 2:
            changewifi(1)
            print("5G-3 -> 5G-2")
            nnn = 2
        time.sleep(0.1)
