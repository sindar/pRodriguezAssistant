# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
# Based on https://gist.github.com/nitaku/10d0662536f37a087e1b

from http.server import HTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus
import json
import time

class _RequestHandler(BaseHTTPRequestHandler):
    POST_callback = None
    
    def _set_headers(self):
        self.send_response(HTTPStatus.OK.value)
        self.send_header('Content-type', 'application/json')
        # Allow requests from any origin, so CORS policies don't
        # prevent local development.
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        response = json.dumps({'bite my shiny': 'metal ass', 'received': 'ok'})
        response = bytes(response, 'utf-8')
        self.wfile.write(response)

    def do_POST(self):
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))
        self._set_headers()
        self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
        
        if _RequestHandler.POST_callback:
            _RequestHandler.POST_callback(message['type'])

    def do_OPTIONS(self):
        # Send allow-origin header for preflight POST XHRs.
        self.send_response(HTTPStatus.NO_CONTENT.value)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST')
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        self.end_headers()

def run_server():
    server_address = ('', 8008)
    httpd = HTTPServer(server_address, _RequestHandler)
    print('serving at %s:%d' % server_address)
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
