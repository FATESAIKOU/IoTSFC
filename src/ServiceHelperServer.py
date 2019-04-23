"""
The program for ServiceHelper to provide service.

@author: FATESAIKOU
@date  : 03/06/2019
"""

import json
import sys

from urllib import parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from ServiceHelperLib.Router import Router

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # arg parse from self.path
        parse_raw = parse.parse_qs(parse.urlsplit(self.path).query)
        action = parse_raw['action'][0]

        if 'args' in parse_raw.keys():
            args = json.loads(parse_raw['args'][0])
        else:
            args = {}

        # do request
        result = Router.Route(action, args)

        # write out
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(result), 'utf-8'))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def run():
    port = int(sys.argv[1])

    service_address = ('', port)
    httpd = ThreadedHTTPServer(service_address, RequestHandler)

    print('start service')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
