# Local server for the model renderer: serves layers/ and render/, saves POSTed PNGs.
import http.server, os, sys, urllib.parse, json

ROOT = os.path.dirname(os.path.abspath(__file__))
LAYERS = os.path.join(os.path.dirname(ROOT), 'layers')
OUT = os.path.join(ROOT, 'out')
os.makedirs(OUT, exist_ok=True)


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype='application/octet-stream'):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
        if p == '/':
            p = '/render.html'
        if p.startswith('/L/'):
            f = os.path.normpath(os.path.join(LAYERS, p[3:]))
            base = LAYERS
        elif p == '/done':
            return self._send(200, json.dumps(sorted(x[:-4] for x in os.listdir(OUT))).encode(), 'application/json')
        else:
            f = os.path.normpath(os.path.join(ROOT, p.lstrip('/')))
            base = ROOT
        if not f.startswith(base) or not os.path.isfile(f):
            return self._send(404, b'not found', 'text/plain')
        ct = {'.html': 'text/html; charset=utf-8', '.json': 'application/json', '.png': 'image/png', '.js': 'text/javascript'}.get(os.path.splitext(f)[1], 'application/octet-stream')
        self._send(200, open(f, 'rb').read(), ct)

    def do_POST(self):
        p = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
        n = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(n)
        if p.startswith('/save/'):
            name = os.path.basename(p[6:])
            if body.startswith(b'data:'):
                import base64
                body = base64.b64decode(body.split(b',', 1)[1])
            open(os.path.join(OUT, name), 'wb').write(body)
            return self._send(200, b'ok', 'text/plain')
        if p == '/log':
            with open(os.path.join(ROOT, 'render.log'), 'ab') as f:
                f.write(body + b'\n')
            return self._send(200, b'ok', 'text/plain')
        self._send(404, b'no', 'text/plain')


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    http.server.ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
