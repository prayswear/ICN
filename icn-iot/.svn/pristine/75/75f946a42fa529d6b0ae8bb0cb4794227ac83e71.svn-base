import json
import socket

gncar_ip = '192.168.100.150'
gncar_port = 5000
gncar_port_my = 5001


def sendgncar_packet(dst_ip, dsp_port, packet):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(packet.encode('utf-8'),(dst_ip,dsp_port))
    except socket.error as e:
        logger.error(e)
    finally:
        sock.close()

def getgncar_packet():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0',gncar_port_my))
    data, address = s.recvfrom(2048)
    eeuuiidd = data['params']['contentEuid']
    return eeuuiidd
    s.close()

def nccar_getguid(xxx):
    orip = {"jsonrpc": "2.0", "method": "Register", "params": {"type": "content", "Name": xxx, "PubKey": "-----public key-----4de3rqwe3-----end public key-----", "contentNa": {"pofSwEuid": "", "port": "", "controllerDomainId": ""}}, "id": 5}
    pstr = json.dumps(orip)
    sendgncar_packet(gncar_ip, gncar_port, pstr)

