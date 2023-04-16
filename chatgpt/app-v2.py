
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

configs = {
    'config1': {
        'PrivateKey': '...',
        'Address': '...',
        'DNS': '...',
        # ...
    },
    'config2': {
        'PrivateKey': '...',
        'Address': '...',
        'DNS': '...',
        # ...
    },
}

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/configs':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(list(configs.keys())).encode('utf-8'))
        elif self.path.startswith('/configs/'):
            config_name = self.path.split('/')[-1]
            if config_name in configs:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(configs[config_name]).encode('utf-8'))
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def do_PUT(self):
        if self.path.startswith('/configs/'):
            config_name = self.path.split('/')[-1]
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            new_config = json.loads(body)
            if config_name in configs:
                configs[config_name] = new_config
                self.send_response(200)
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith('/configs/'):
            config_name = self.path.split('/')[-1]
            if config_name in configs:
                del configs[config_name]
                self.send_response(200)
            else:
                self.send_error(404)
        else:
            self.send_error(404)

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f'Starting server at http://{server_address[0]}:{server_address[1]}...')
    httpd.serve_forever()
