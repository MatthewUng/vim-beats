import requests
import pprint
from credentials import CLIENT_ID, CLIENT_SECRET

token = ''
def get_token():
    global token
    url = "https://accounts.spotify.com/api/token"
    header = {
            "Content-Type": "application/x-www-form-urlencoded"
            }
    data = {
            "grant_type":"client_credentials",
            "client_id": f"{CLIENT_ID}",
            "client_secret": "{CLIENT_SECRET}",
            }

    resp = requests.post(url, headers=header, data=data)
    json = resp.json()
    token = json['access_token']
    print('json:',resp.json())

def get_artist():
    # alina baraz
    artist_id = '6hfwwpXqZPRC9CsKI7qtv1'
    url = 'https://api.spotify.com/v1/artists/' + artist_id
    headers = {
            "Authorization": "Bearer "+token
            }

    resp = requests.get(url, headers=headers)
    pprint.pprint(resp.json())

get_token()
print('token', token)
get_artist()
