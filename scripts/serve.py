"""Local static preview only; no mail-sending endpoint."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import argparse,csv
from urllib.parse import urlsplit
root=Path(__file__).resolve().parents[1]/'website'
with (root.parent/'content/url-map.csv').open() as f:
    redirects={r['old_path']:r['new_path'] for r in csv.DictReader(f)}
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)
    def redirect_legacy(self):
        parsed=urlsplit(self.path)
        if parsed.path not in redirects:return False
        self.send_response(301)
        self.send_header('Location',redirects[parsed.path]+('?'+parsed.query if parsed.query else ''))
        self.send_header('Content-Length','0')
        self.end_headers()
        return True
    def do_GET(self):
        if not self.redirect_legacy():super().do_GET()
    def do_HEAD(self):
        if not self.redirect_legacy():super().do_HEAD()
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','strict-origin-when-cross-origin')
        self.send_header('Cache-Control','no-cache')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; media-src 'self' blob:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
        super().end_headers()
    def send_error(self,code,message=None,explain=None):
        if code==404 and (root/'404.html').exists():
            body=(root/'404.html').read_bytes();self.send_response(404);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        else:super().send_error(code,message,explain)
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=4173);p.add_argument('--host',default='127.0.0.1');a=p.parse_args()
print(f'KWS preview: http://{a.host}:{a.port}',flush=True)
ThreadingHTTPServer((a.host,a.port),Handler).serve_forever()
