#!/usr/local/bin/python3
import http.server
import os
import time
import threading

from auth import get_auth_code, do_access_token
from config import REFRESH_TOKEN_FILE, AUTH_TOKEN_FILE
from config import save_auth_token, save_refresh_token

PORT = 8080

# determines when to shutdown the server
# this is set when the auth code is received from spotify
done = False
# global variable holding onto the code itself
code = None

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global done, code

        prefix = r'/?code='
        if len(self.path) < len(prefix): return
        if self.path[:len(prefix)] != prefix: return
        code = self.path[len(prefix):]

        done = True

        message = "Authorization complete! Close the tab and return to the terminal"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(message.encode())))
        self.end_headers()
        self.wfile.write(message.encode())

        self.flush_headers()

if __name__ == '__main__':
    if os.path.isfile(AUTH_TOKEN_FILE):
        print("Auth token file already exists.  Skipping authorization...")
        exit()

    server_addr = ('', PORT)
    httpd = http.server.HTTPServer(server_addr, SimpleHandler)
    server_thread = threading.Thread(None, httpd.serve_forever)
    server_thread.start()


    get_auth_code()

    while True:
        if done: 
            httpd.server_close()
            httpd.shutdown()
            break
        time.sleep(1)

    server_thread.join()

    auth_token, refresh_token = do_access_token(code)

    save_auth_token(auth_token)
    save_refresh_token(refresh_token)

