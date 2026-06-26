from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

request_token = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global request_token

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        request_token = params.get("request_token", [None])[0]

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Login successful. You can close this window.")

server = HTTPServer(("localhost", 8000), CallbackHandler)

threading.Thread(target=server.serve_forever, daemon=True).start()