import argparse
import pprint
import sys

from lib.config import get_auth_token
from lib.utils import get_playlist_id
import lib.controls as controls


COMMANDS = [
        'play',
        'pause',
        'next',
        'prev',
        'get-devices',
        'currently-playing',
        'current-song',
        'get-playlist'
]

def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=COMMANDS)
    parser.add_argument('-d', '--device_id', default=None)
    parser.add_argument('-c', '--context_uri', default=None)
    parser.add_argument('--debug', default=None, action='store_true')
    return parser

def print_if_debug(*print_args, **print_kwargs):
    global args
    if args.debug:
        print(*print_args, **print_kwargs)

if __name__ == '__main__':
    parser = setup_parser()
    args = parser.parse_args()

    auth_token = get_auth_token()

    if args.command == 'play':
        resp = controls.start_playback(
                auth_token, 
                device_id=args.device_id,
                context_uri=args.context_uri)
        if resp.status_code >= 400:
            print_if_debug(resp.json())
        print_if_debug(resp.status_code)
    elif args.command == 'pause':
        resp = controls.pause_playback(auth_token)
        if resp.status_code >= 400:
            print_if_debug(resp.json())
        print_if_debug(resp.status_code)
    elif args.command == 'next':
        resp = controls.next_song(auth_token)
        print_if_debug(resp.status_code)
    elif args.command == 'prev':
        resp = controls.prev_song(auth_token)
        print_if_debug(resp.status_code)
    elif args.command == 'get-devices':
        resp = controls.get_devices(auth_token)
        print_if_debug(resp.status_code)
        pprint.pprint(resp.json())
    elif args.command == 'currently-playing':
        resp = controls.get_currently_playing(auth_token) 
        pprint.pprint(resp.json())
    elif args.command == 'current-song':
        song = controls.current_song(auth_token)
        print(song, end='')
    elif args.command == 'get-playlist':
        playlist = controls.get_playlist(auth_token, get_playlist_id(args.context_uri))
        print(playlist, end='')
    else:
        exit(1)

