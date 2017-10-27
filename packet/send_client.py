import socket
import threading
import logging.config
from packet import *
import binascii
import hashlib
import time
import subprocess

LAN_UDP_MTU = 1472
STD_UDP_MTU = 548
UDP_MTU = STD_UDP_MTU
ICN_MTU = UDP_MTU - 36  # 36 is len of none-tlv icn head
ICN_TEMP_MTU = ICN_MTU - 8  # 8 is len of tlv
ICN_CONTENT_MTU = ICN_TEMP_MTU - 1 - 16  # 1 is icn type, 16 is content euid
icn_data_reply_type = '09'

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')

selfeuid = '7ee30ed78da46257a17047254b7d6a4b'
pi1_euid = '2613f2a93a0683bdc6260edfcfec6d76'
pi2_euid = 'b498dce7ea1f7a1a1b11a48dfef58303'
cm1_euid = 'b13ded0762217339428aba5d508ddf5c'
gnrs_addr = ('192.168.47.16', 8899)
cmd_port = 35000
data_port = 36000


def do_request_without_gnrs():
    cmd_port = 35000
    video_content_euid = 'ab92b7014f2887ea05450143f4c9ad01'
    temprature_content_euid = ''
    # content_na = ('192.168.1.21', cmd_port)
    content_na = ('192.168.2.100', cmd_port)
    # content_na = ('192.168.3.100', cmd_port)
    request_packet = ICNPacket()
    request_packet.setHeader('ffffac7196110678d84d03687eab03fb', 'b13ded0762217339428aba5d508ddf5c', '00')
    request_packet.setPayload(binascii.a2b_hex('0d' + video_content_euid))
    request_packet.fill_packet()
    request_packet.print_packet()
    send_cmd_packet(request_packet.grap_packet(), content_na, False)


def int2bytes(num, length):
    # length is the bytes you want to get
    num_hex_str = hex(num).replace('0x', '')
    format_str = '0' * (length * 2 - len(num_hex_str)) + num_hex_str
    return binascii.a2b_hex(format_str)


def send_cmd_packet(data, address, flag):
    if len(data) > LAN_UDP_MTU:
        return None
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(str(address))
    sock.sendto(data, address)
    sock.settimeout(1)
    # reply, remote_addr = sock.recvfrom(1024)
    # print(reply.decode('utf-8'))
    try:
        if flag == True:
            reply, remote_addr = sock.recvfrom(1024)
            p = ICNPacket()
            p.gen_from_hex(reply)
            p.print_packet()
            sock.close()
            return p
            # logger.info(reply.decode('utf-8'))
    except socket.timeout:
        logger.warning('Timeout and no reply')
    finally:
        sock.close()


def send_data_packet(packet, address):
    # data is like icn_head + '09' + euid + realdata
    send_times = 1
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    content_euid_hex = packet.payload[1:17]
    temp_packet = ICNPacket()
    temp_packet.setHeader(packet.src_guid, packet.dst_guid, '00')
    DATA_SIZE_PER_UDP = ICN_CONTENT_MTU  # 1411
    data2send = packet.grap_packet()
    data_size = len(data2send)
    current_id = hashlib.sha1(data2send).hexdigest()[0:4]  # 2 bytes
    sent_size = 0
    point = 0
    count = 0
    while sent_size < data_size:
        remain_size = data_size - sent_size
        send_size = DATA_SIZE_PER_UDP if remain_size > DATA_SIZE_PER_UDP else remain_size
        temp_packet.setTLV(binascii.a2b_hex(current_id) + int2bytes(data_size, 4) + int2bytes(count, 2))
        send_data = data2send[point:point + send_size]
        point += send_size
        sent_size += send_size
        count += 1
        temp_packet.setPayload(binascii.a2b_hex(icn_data_reply_type) + content_euid_hex + send_data)
        temp_packet.fill_packet()
        logger.info(temp_packet.print_packet_without_payload())
        sock.sendto(temp_packet.grap_packet(), address)
        if count == 1:
            time.sleep(0.1)
    send_times -= 1
    while send_times > 0:
        sent_size = DATA_SIZE_PER_UDP
        point = DATA_SIZE_PER_UDP
        count = 1
        while sent_size < data_size:
            remain_size = data_size - sent_size
            send_size = DATA_SIZE_PER_UDP if remain_size > DATA_SIZE_PER_UDP else remain_size
            temp_packet.setTLV(binascii.a2b_hex(current_id) + int2bytes(data_size, 4) + int2bytes(count, 2))
            send_data = data2send[point:point + send_size]
            point += send_size
            sent_size += send_size
            count += 1
            temp_packet.setPayload(binascii.a2b_hex(icn_data_reply_type) + content_euid_hex + send_data)
            temp_packet.fill_packet()
            logger.info(temp_packet.print_packet_without_payload())
            sock.sendto(temp_packet.grap_packet(), address)
        send_times -= 1
    sock.close()


def query_gnrs(euid):
    gnrs_reply_listen_port = 12321
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)
    sock.bind(('0.0.0.0', gnrs_reply_listen_port))
    result = None
    try:
        reply, gnrs_addr = sock.recvfrom(1024)
        p = ICNPacket()
        p.gen_from_hex(reply)
        payload = binascii.b2a_hex(p.payload).decode('utf-8')
        if payload[0:2] == '04' and payload[2:34] == euid:
            result = socket.inet_ntoa(payload[34:42])
    except socket.timeout:
        logger.warning('GNRS timeout...')
    finally:
        sock.close()
        return result


def gnrs_sign_up(selfna):
    selfna_hex = socket.inet_aton(selfna)
    print(selfna_hex)
    time_stamp = hex(int(time.time())).replace('0x', '')
    sign_p = ICNPacket()
    sign_p.setHeader(selfeuid, cm1_euid, '00')
    sign_p.setPayload(binascii.a2b_hex('01' + selfeuid) + selfna_hex + binascii.a2b_hex(time_stamp + '01'))
    sign_p.fill_packet()
    sign_p.print_packet()
    recv_p = send_cmd_packet(sign_p.grap_packet(), gnrs_addr, True)
    p_type = binascii.b2a_hex(recv_p.payload[:1]).decode('utf-8')
    p_euid = binascii.b2a_hex(recv_p.payload[1:17]).decode('utf-8')
    p_ack = binascii.b2a_hex(recv_p.payload[17:18]).decode('utf-8')
    if p_type == '02' and p_euid == selfeuid and p_ack == '01':
        logger.info('gnrs sign up ok')
        return True
    else:
        logger.error('gnrs sign up wrong')
        return False


def start_request():
    content_euid = 'ab92b7014f2887ea05450143f4c9ad01'
    # content_euid = 'ecaca102a95a828d0b081cefd0747a5d'
    # content_euid='f80af4ee95da779efde6dc28329438f3'
    # content_euid='2a22cec2eaaa0e9ea91743a3226064b8'

    query_packet = ICNPacket()
    query_packet.setHeader(selfeuid, cm1_euid, '00')
    query_packet.setPayload(binascii.a2b_hex('03' + content_euid + '00'))
    query_packet.fill_packet()
    query_packet.print_packet()

    # flag=3
    # while flag>0:
    recv_p = send_cmd_packet(query_packet.grap_packet(), gnrs_addr, True)
    p_type = binascii.b2a_hex(recv_p.payload[:1]).decode('utf-8')
    if p_type == '04':
        recv_euid = binascii.b2a_hex(recv_p.payload[1:17])
        print('recv_euid:' + recv_euid.decode('utf-8'))
        print(binascii.b2a_hex(recv_p.payload[17:21]))
        recv_na = socket.inet_ntoa(recv_p.payload[17:21])
        print('recv_na:' + recv_na)
    else:
        logger.error('receive wrong packet!')
    # recv_na='192.168.2.234'
    # content_na = (query_gnrs(content_euid), cmd_port)
    if not recv_na == None and recv_euid.decode('utf-8') == content_euid:
        # if True:
        logger.info('content_na is ' + str(recv_na))
        request_packet = ICNPacket()
        request_packet.setHeader(selfeuid, pi1_euid, '00')
        request_packet.setPayload(binascii.a2b_hex('0d' + content_euid))
        request_packet.fill_packet()
        request_packet.print_packet()
        send_cmd_packet(request_packet.grap_packet(), (recv_na, cmd_port), False)
    else:
        logger.error('can not query na!')


def auto_request():
    start_request()
    mac_list = ["88:10:36:30:30:f1", "88:10:36:30:41:61", "88:10:36:30:40:ec"]
    ip_list = ['192.168.10.104', '192.168.2.104', '192.168.3.104']
    state = [0, 0, 0, 0, 0]
    state_old = [0, 0, 0, 0, 0]
    cmd = 'iw dev wlp5s0 station dump | grep Station'
    nowna = 'None'
    while True:
        obj = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        obj.wait()
        sizeofmac_list = len(mac_list)
        for i in range(sizeofmac_list):
            state_old[i] = state[i]
        lines = obj.stdout.readlines()
        state = [0, 0, 0, 0, 0]
        for i in range(sizeofmac_list):
            for strs in lines:
                if str(strs).find(mac_list[i]) > 0:
                    state[i] = 1
                    break
        for i in range(sizeofmac_list):
            if state[i] > state_old[i]:
                lastna = nowna
                nowna = ip_list[i]
                print("------%s->%s-------" % (lastna, nowna))
                print("AP %d - %s Linked! NA is %s" % (i, mac_list[i], ip_list[i]))
                if not lastna == 'None':
                    time.sleep(2)
                    print("--------NA:%s->%s" % (lastna, nowna))
                    flag = False
                    while flag == False:
                        flag = gnrs_sign_up(nowna)
                        logger.info('Sign in ' + nowna + ' ok')
                    start_request()
        time.sleep(0.1)


if __name__ == '__main__':
    # start_request()
    # do_request_without_gnrs()
    auto_request()
    # flag = gnrs_sign_up('192.168.3.104')
    # print(flag)
