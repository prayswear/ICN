from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import io, shutil, datetime
import logging.config
import signature
import dbtool

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


class ncsRequestHandler(BaseHTTPRequestHandler):
    def is_hrn_exist(self, hrn):
        if not mydb.query('NCS_tbl', {'hrn': hrn}) == None:
            return True
        else:
            return False

    def get_guid(self, hrn, type):
        if self.is_hrn_exist(hrn):
            logger.warning('HRN: ' + hrn + ' is already exist, get guid failed.')
            guid = ''
        else:
            guid = signature.gen_guid(hrn)
            mydb.add('NCS_tbl', {'hrn': hrn, 'guid': guid, 'type': type})
        return guid

    def query_hrn(self, guid):
        result = mydb.query('NCS_tbl', {'guid': guid})
        if not result == None:
            hrn = result['hrn']
        else:
            hrn = ''
        return hrn

    def query_guid(self, hrn):
        result = mydb.query('NCS_tbl', {'hrn': hrn})
        if not result == None:
            guid = result['guid']
        else:
            guid = ''
        return guid

    def query_type(self, guid):
        result = mydb.query('NCS_tbl', {'guid': guid})
        if not result == None:
            type = result['type']
        else:
            type = ''
        return type

    def do_GET(self):
        querypath = parse.urlparse(self.path)
        filepath = querypath.path
        queryString = parse.unquote(querypath.query)
        params = parse.parse_qs(queryString)

        if filepath == '/getguid':
            result = self.get_guid(params['hrn'][0], params['type'][0])
        elif filepath == '/queryhrn':
            result = self.query_hrn(params['guid'][0])
        elif filepath == '/queryguid':
            result = self.query_guid(params['hrn'][0])
        elif filepath == '/querytype':
            result = self.query_type(params['guid'][0])
        else:
            result = ''

        try:
            r_str = str(result)
            encoded = ''.join(r_str).encode('utf-8')
            f = io.BytesIO()
            f.write(encoded)
            f.seek(0)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            shutil.copyfileobj(f, self.wfile)
        except IOError:
            self.send_error(404)
            self.end_headers()


def start_server(ip, port):
    logger.info('Starting server at :' + ip + ':' + str(port))
    server_address = (ip, port)
    httpd = HTTPServer(server_address, ncsRequestHandler)
    logger.info('Running server...')
    httpd.serve_forever()


if __name__ == '__main__':
    ncs_ip = '127.0.0.1'
    ncs_port = 12701
    dbip = '127.0.0.1'
    dbport = 27017
    dbname = 'ncs'
    mydb = dbtool.myDB(dbip, dbport, dbname)
    start_server(ncs_ip, ncs_port)
