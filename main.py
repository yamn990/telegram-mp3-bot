import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), DummyHandler)
    server.serve_forever()

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server).start()
    main()
