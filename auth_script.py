#!/usr/local/bin/python3

import http.server
import os
import time
import threading

from lib.auth import get_auth_code, do_access_token
from lib.config import REFRESH_TOKEN_FILE, AUTH_TOKEN_FILE
from lib.config import save_auth_token, save_refresh_token

PORT = 8080
REDIRECT_URI =  "http://localhost:8080"

# determines when to shutdown the server
# this is set when the auth code is received from spotify
done = False
# global variable holding onto the authorization code itself
code = None
# File storing client id and client secret
CREDENTIALS_FILE = r'lib/credentials.py'

def create_credentials(client_id, client_secret):
    with open(CREDENTIALS_FILE, 'w') as f:
        f.write(f"CLIENT_ID = r'{client_id}'")
        f.write(f"CLIENT_SECRET = r'{client_secret}'")

# Simple HTTP server to obtain the access code after user authorization
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

    if not os.path.isfile(CREDENTIALS_FILE):
        client_id = input("Input client id: ")
        client_secret = input("Input client secret: ")

        create_credentials(client_id, client_secret)

    server_addr = ('', PORT)
    httpd = http.server.HTTPServer(server_addr, SimpleHandler)
    server_thread = threading.Thread(None, httpd.serve_forever)
    server_thread.start()

    get_auth_code(REDIRECT_URI)

    while True:
        if done: 
            httpd.server_close()
            httpd.shutdown()
            break
        time.sleep(1)

    server_thread.join()

    auth_token, refresh_token = do_access_token(code, REDIRECT_URI)

    save_auth_token(auth_token)
    save_refresh_token(refresh_token)

    print("Authorization success!")

