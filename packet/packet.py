import logging.config
import binascii

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


class ICNPacket():
    def __init__(self):
        self.src_guid = ''  #
        self.dst_guid = ''
        self.service_type = ''
        self.header_len = 36  # 0-255
        self.header_checksum = ''
        self.tlv = ''
        self.payload = b''

    def setHeader(self, src_guid='', dst_guid='', service_type=''):
        self.src_guid = src_guid
        self.dst_guid = dst_guid
        self.service_type = service_type

    def setTLV(self, tlv):
        self.tlv = tlv

    def setPayload(self, payload):
        self.payload = payload

    def checksum(self, data):
        length = len(data)
        checksum = 0
        for i in range(0, length):
            checksum += int.from_bytes(data[i:i + 1], 'little', signed=False)
        checksum &= 0xffff
        checksum_hex = hex(checksum).replace('0x', '')
        result = '0' * (4 - len(checksum_hex)) + checksum_hex
        return result

    def fill_packet(self):
        self.header_len = 36 + int(len(self.tlv) / 2)
        self.header_checksum = self.do_checksum()

    def do_checksum(self):
        src_guid_hex = binascii.a2b_hex(self.src_guid)
        dst_guid_hex = binascii.a2b_hex(self.dst_guid)
        service_type_hex = binascii.a2b_hex(self.service_type)
        header_len_hex = binascii.a2b_hex(hex(self.header_len).replace('0x', ''))
        tlv_hex = binascii.a2b_hex(self.tlv)
        payload_hex = self.payload
        other = src_guid_hex + dst_guid_hex + service_type_hex + header_len_hex
        return self.checksum(other)

    def check_checksum(self):
        if self.header_checksum == self.do_checksum():
            return True
        else:
            return False

    def print_packet(self):
        logger.info(
            '\n###ICN PACKET###'
            '\n# src guid: ' + self.src_guid +
            '\n# dst_guid: ' + self.dst_guid +
            '\n# service type: ' + self.service_type +
            '\n# header length: ' + str(self.header_len) +
            '\n# header checksum: ' + self.header_checksum +
            '\n# tlv: ' + self.tlv +
            '\n# payload: ' + binascii.b2a_hex(self.payload).decode('utf-8') +
            '\n################')

    def grap_packet(self):
        src_guid_hex = binascii.a2b_hex(self.src_guid)
        dst_guid_hex = binascii.a2b_hex(self.dst_guid)
        service_type_hex = binascii.a2b_hex(self.service_type)
        header_len_hex = binascii.a2b_hex(hex(self.header_len).replace('0x', ''))
        header_checksum_hex = binascii.a2b_hex(self.header_checksum)
        tlv_hex = binascii.a2b_hex(self.tlv)
        hex_result = src_guid_hex + dst_guid_hex + service_type_hex + header_len_hex + header_checksum_hex + tlv_hex + self.payload
        return hex_result

    def gen_from_hex(self, data):
        self.src_guid = binascii.b2a_hex(data[0:16]).decode('utf-8')
        self.dst_guid = binascii.b2a_hex(data[16:32]).decode('utf-8')
        self.service_type = binascii.b2a_hex(data[32:33]).decode('utf-8')
        self.header_len = int(binascii.b2a_hex(data[33:34]), 16)
        self.header_checksum = binascii.b2a_hex(data[34:36]).decode('utf-8')
        self.tlv = binascii.b2a_hex(data[36:self.header_len]).decode('utf-8')
        self.payload = data[self.header_len:len(data)]
