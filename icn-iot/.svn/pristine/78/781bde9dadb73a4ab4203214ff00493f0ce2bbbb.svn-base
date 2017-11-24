import hashlib


def gen_guid(str):
    return hashlib.sha1(str.encode('utf-8')).hexdigest()[0:32]


if __name__ == '__main__':
    # the hex digest is a 40-hex string, means 20 byte
    x = hashlib.sha1('lijq'.encode('utf-8'))
    print(x.hexdigest())
    print(type(x.hexdigest()))
    guid_p = x.hexdigest()[0:16]
    print(guid_p)
