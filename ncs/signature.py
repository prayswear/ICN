import hashlib
import time

def gen_guid(str):
    return hashlib.sha1(str.encode('utf-8')).hexdigest()[0:32]


if __name__ == '__main__':
    # the hex digest is a 40-hex string, means 20 byte
    x = hashlib.sha1('pi2'.encode('utf-8'))
    print(x.hexdigest())
    print(type(x.hexdigest()))
    guid_p = x.hexdigest()[0:32]
    print(guid_p)
    pi1='2613f2a93a0683bdc6260edfcfec6d76'
    pi2='b498dce7ea1f7a1a1b11a48dfef58303'
    print(hex(int(time.time())))
    num_hex_str = hex(int(time.time())).replace('0x', '')
    print(type(num_hex_str))
