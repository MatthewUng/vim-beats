import base64 as b64
import requests
from credentials import CLIENT_ID, CLIENT_SECRET

scopes = [
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
        "app-remote-control",
        "streaming",
        "playlist-read-private",
        "user-library-read",
        ]

REDIRECT_URI =  "http://localhost:8080"

def convert_b64(s):
    bytes = s.encode('ascii')
    b64_bytes = b64.b64encode(bytes)
    b64_message = b64_bytes.decode('ascii')
    return b64_message

def get_auth_code():
    auth_params = {
            "client_id": CLIENT_ID,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": ' '.join(scopes),
            }
    auth_url = 'https://accounts.spotify.com/authorize'
    resp = requests.get(auth_url, params=auth_params)
    print('Authorize spotify usage by clicking the link: ', resp.url)


def do_access_token(code):
    url = "https://accounts.spotify.com/api/token"
    data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            }

    headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic "+convert_b64(f"{CLIENT_ID}:{CLIENT_SECRET}"),
            }
    resp = requests.post(url, headers=headers, data=data)
    json = resp.json()
    return json['access_token'], json['refresh_token']

def do_refresh_token(refresh_token):
    url = "https://accounts.spotify.com/api/token"
    data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            }

    headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic "+convert_b64(f"{CLIENT_ID}:{CLIENT_SECRET}"),
            }
    resp = requests.post(url, headers=headers, data=data)
    json = resp.json()
    return json['access_token']
