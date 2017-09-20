import io
import logging.config
import shutil
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse

from util import dbtool

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('myLogger')


class gnrsRequestHandler(BaseHTTPRequestHandler):
    def do_sign_in(self, guid, na):
        nas = mydb.query('GUID_NA_tbl', {'guid': guid})
        if nas == None:
            item = {'guid': guid, 'nas': str([na])}
            mydb.add('GUID_NA_tbl', item)
        else:
            nas_temp = list(eval(nas['nas']))
            flag = True
            for i in nas_temp:
                if na == i:
                    flag = False
            if flag == True:
                nas_temp.append(na)
                mydb.update('GUID_NA_tbl', {'guid': guid}, {'nas': str(nas_temp)})
        return 'OK'

    def do_query(self, guid):
        nas = mydb.query('GUID_NA_tbl', {'guid': guid})
        if not nas == None:
            nas = nas['nas']
        if nas == None:
            nas = ''
        return nas

    def do_GET(self):
        querypath = parse.urlparse(self.path)
        filepath = querypath.path
        queryString = parse.unquote(querypath.query)
        params = parse.parse_qs(queryString)
        result = ''
        if filepath == '/signup':
            result = self.do_sign_in(params['guid'][0], params['na'][0])
        elif filepath == '/querynas':
            result = self.do_query(params['guid'][0])
        else:
            pass

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
            self.send_error(404, 'Not Found: %s' % self.path)


def start_server(ip, port):
    logger.info('Starting server at :' + ip + ':' + str(port))
    server_address = (ip, port)
    httpd = HTTPServer(server_address, gnrsRequestHandler)
    logger.info('Running server...')
    httpd.serve_forever()


if __name__ == '__main__':
    ncs_ip = '127.0.0.1'
    ncs_port = 12700
    dbip = '127.0.0.1'
    dbport = 27017
    dbname = 'gnrs'
    mydb = dbtool.myDB(dbip, dbport, dbname)
    start_server(ncs_ip, ncs_port)
