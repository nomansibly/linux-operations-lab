"""Local-only HTTP service for controlled troubleshooting exercises."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/health':
            code, body = 404, {'status': 'route_not_found'}
        elif self.server.fault_file.exists():
            code, body = 503, {'status': 'unavailable', 'reason': 'simulated_dependency_failure'}
        else:
            code, body = 200, {'status': 'ok'}
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=int, default=8088)
    p.add_argument('--fault-file', type=Path, default=Path('runtime/dependency.failed'))
    a = p.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', a.port), Handler)
    server.fault_file = a.fault_file
    print(json.dumps({'event': 'listening', 'host': '127.0.0.1', 'port': server.server_port}), flush=True)
    server.serve_forever()
