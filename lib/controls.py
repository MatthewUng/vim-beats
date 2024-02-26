import requests
import pprint
import functools

from lib.credentials import CLIENT_ID, CLIENT_SECRET
from lib.auth import do_refresh_token
from lib.config import get_refresh_token, save_auth_token
from lib.api import Song, Playlist
from lib.json_to_obj import json_to_song, json_to_playlist


def retry_on_401(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        resp = f(*args, **kwargs)
        if resp.status_code != 401: return resp

        refresh_token = get_refresh_token()
        new_access_token = do_refresh_token(refresh_token)
        save_auth_token(new_access_token)

        resp = f(*args, **kwargs)
        new_args = list(args)
        new_args[0] = new_access_token
        return f(*new_args, **kwargs)

    return wrap


def add_auth_header(token, headers={}):
    out = headers.copy()
    out["Authorization"]= "Bearer "+token
    return out

@retry_on_401
def fetch_profile(token):
    url = "https://api.spotify.com/v1/me"

    return requests.get(url, headers=add_auth_header(token))

@retry_on_401
def get_currently_playing(token):
    url = r'https://api.spotify.com/v1/me/player/currently-playing'
    return requests.get(url, headers=add_auth_header(token))

@retry_on_401
def pause_playback(token):
    url = 'https://api.spotify.com/v1/me/player/pause'
    return requests.put(url, headers=add_auth_header(token))

@retry_on_401
def start_playback(token, device_id=None, context_uri=None):
    url = 'https://api.spotify.com/v1/me/player/play'
    params = {}
    if device_id:
        params['device_id'] = device_id
    data = {}
    if context_uri:
        data['context_uri'] = context_uri
    return requests.put(url, 
                        headers=add_auth_header(token),
                        params=params,
                        json=data)

@retry_on_401
def get_devices(token):
    url = r'https://api.spotify.com/v1/me/player/devices'
    return requests.get(url, headers=add_auth_header(token))

@retry_on_401
def get_playback_state(token):
    url = r'https://api.spotify.com/v1/me/player'
    return requests.get(url, headers=add_auth_header(token))

@retry_on_401
def next_song(token):
    url = 'https://api.spotify.com/v1/me/player/next'
    return requests.post(url, headers=add_auth_header(token))

@retry_on_401
def prev_song(token):
    url = 'https://api.spotify.com/v1/me/player/previous'
    return requests.post(url, headers=add_auth_header(token))

@retry_on_401
def get_user_albums(token):
    url = r'https://api.spotify.com/v1/me/albums'
    return requests.get(url, headers=add_auth_header(token))

@retry_on_401
def set_volume(token, volume_percent):
    url = r'https://api.spotify.com/v1/me/player/volume'
    data = {
            'volume_percent': volume_percent,
            }
    return requests.put(url,
                        headers=add_auth_header(token),
                        params=data)

def get_playlist(token, playlist_id='59nrpzDIGSd5EZ1ApjKRCE'):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    FIELDS = [
            'name',
            'description',
            'owner',
            'id'
            ]

    @retry_on_401
    def send_req():
        return requests.get(url,
                            headers=add_auth_header(token),
                            params={'fields': ','.join(FIELDS)})

    js = send_req().json()
    return Playlist(js['name'], js['description'], js['owner']['display_name'], js['id'])

@retry_on_401
def queue_track(token, track):
    url = f'https://api.spotify.com/v1/me/player/queue'
    data = {
        "uri": track,
            }
    return requests.post(url,
                        headers=add_auth_header(token),
                        params=data)

@retry_on_401
def search(token, query, params={}):
    url = f'https://api.spotify.com/v1/search'
    params['q'] = query
    return requests.get(url,
                        headers=add_auth_header(token),
                        params=params)

def search_song(token, query):
    params = {
            'type': 'track'
            }

    resp = search(token, query, params)
    js = resp.json()
    out = []
    for track in js['tracks']['items']:
        name = track['name']
        artists = [x['name'] for x in track['artists']]
        album = track['album']
        uri = track['uri']

        out.append(Song(name, artists, album, uri))
    return out

def current_song(token):
    resp = get_currently_playing(token)

    js = resp.json()
    js_track = js['item']

    return json_to_song(js_track)

def get_playlists(token):
    @retry_on_401
    def send_req(offset=None):
        url = r'https://api.spotify.com/v1/me/playlists'
        params = { 'limit': 50}
        if offset is not None:
            params['offset'] = int(offset)
        return requests.get(url,
                            headers=add_auth_header(token),
                            params = params)

    tot = -1
    out = []
    while tot == -1 or len(out) != tot:
        resp = send_req(offset=len(out)).json()
        tot = resp['total']
        for playlist in resp['items']:
            out.append(json_to_playlist(playlist))
    return out

def get_recommendations(token, artists, tracks):
    @retry_on_401
    def send_req():
        url = r'https://api.spotify.com/v1/recommendations'
        params = {
                "seed_tracks": tracks,
                "limit": 25
                }
        if tracks:
            if type(artists) == list:
                params['seed_tracks'] = ','.join(tracks)
            else:
                params['seed_tracks'] = tracks

        if artists:
            if type(artists) == list:
                params['seed_artists'] = ','.join(artists)
            else:
                params['seed_artists'] = artists


        return requests.get(url,
                            headers=add_auth_header(token),
                            params=params)
    resp = send_req()
    out = []
    for track in resp.json()['tracks']:
        out.append(json_to_song(track))
    return out
