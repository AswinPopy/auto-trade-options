from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

request_token = None
from state import state

class CallbackHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global request_token

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        state.request_token = params.get("request_token", [None])[0]

        print(f"Received request token: {state.request_token}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(
            b"Login successful. You can close this window."
        )


server = None


def start_callback_server():

    global server

    if server is not None:
        return

    server = HTTPServer(
        ("localhost", 8000),
        CallbackHandler
    )

    threading.Thread(
        target=server.serve_forever,
        daemon=True
    ).start()

    print("Callback server started")