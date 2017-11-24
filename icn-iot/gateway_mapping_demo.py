import pymongo
import logging.config
import dbtool

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('myLogger')

    mytable = {0: 'ID_LUID_tbl', 1: 'GUID_NA_tbl', 2: 'LUID_GUID_tbl'}
    db_ip, db_port = '127.0.0.1', 27017
    db_name = 'GWmapping'
    mydb = dbtool.myDB(db_ip, db_port, db_name)

    username = 'lijq'
    na = '192.168.100.149'
    myluid = '7ee3'
    myguid = '7ee30ed78da46257a17047254b7d6a4bbf6bc01e'

    # add
    mydb.add(mytable[0], {'hrn': 'lijqphone', 'luid': myluid})
    mydb.add(mytable[1], {'guid': myguid, 'na': na})
    mydb.add(mytable[2], {'luid': myluid, 'guid': myguid})

    # query
    result = mydb.query(mytable[2], {'luid': myluid})
    logger.info('Query luid: ' + myluid + ', its guid is ' + str(result))

    # update
    mydb.update(mytable[1], {'guid': myguid}, {'na': '8.8.8.8'})

    # query all
    result = mydb.query_all(mytable[2], {})
    for i in result:
        logger.info(i)

    # remove
    mydb.remove(mytable[0], {'hrn': 'lijqphone'})

    # remove all
    mydb.remove_all(mytable[2])

    mydb.db_close()
    logger.info('Close db connection.')
