import pymongo
import logging.config
import datetime

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


class myDB():
    def __init__(self, ip, port, db_name):
        # init var
        self.ip = ip
        self.port = port
        self.db_name = db_name
        self.db = self.get_db(self.ip, self.port, self.db_name)

    def get_db(self, ip, port, db_name):
        # make connect and get a db entry
        self.db_client = pymongo.MongoClient(ip, port)
        logger.info('Get connection client.')
        db = self.db_client[db_name]
        logger.info('Get database: ' + db_name)
        return db

    def add(self, tbl, item):
        item['lmt'] = datetime.datetime.now()
        self.db[tbl].insert(item)
        logger.info('Add new item: ' + str(item) + ' to ' + tbl)

    def update(self, tbl, condition, value):
        value['lmt'] = datetime.datetime.now()
        self.db[tbl].update(condition, {"$set": value})
        logger.info('Update ' + str(condition) + 'item in ' + tbl)

    def query(self, tbl, condition):
        result = self.db[tbl].find_one(condition)
        logger.info('Find ' + str(condition) + ' item in ' + tbl + ', result is ' + str(result))
        return result

    def query_all(self, tbl, condition):
        result = self.db[tbl].find(condition)
        logger.info('Find all ' + str(condition) + ' item in ' + tbl + ', result is ' + str(result))
        return result

    def remove(self, tbl, condition):
        result = self.db[tbl].remove(condition)
        logger.info('Remove item' + str(condition) + ' item from ' + tbl)

    def remove_all(self, tbl):
        self.db[tbl].remove({})
        logger.info('Remove all data from ' + tbl)

    def db_close(self):
        self.db_client.close()
        logger.info('Close db connection.')
