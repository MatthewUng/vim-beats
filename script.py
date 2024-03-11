import argparse
import pprint
import sys

from lib.config import get_auth_token
from lib.utils import get_playlist_id
import lib.controls as controls
from lib.cache import get_with_ttl, write

from concurrent.futures import ThreadPoolExecutor

COMMANDS = [
        'play',
        'pause',
        'next',
        'prev',
        'get-devices',
        'currently-playing',
        'current-song',
        'get-playlist',
        'queue-song',
        'search',
        'get-playlists',
        'get-recommendations',
        'get-queue',
        'get-featured-playlists',
        'add-tracks',
        'delete-tracks'
]

def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=COMMANDS)
    parser.add_argument('-d', '--device_id', default=None)
    parser.add_argument('-c', '--context_uri', default=None)
    parser.add_argument('-q', '--query', default=None)
    parser.add_argument('--tracks',  nargs='+', default=[])
    parser.add_argument('--no-cache', default=False, action='store_true')
    parser.add_argument('--debug', default=None, action='store_true')
    parser.add_argument('--json', default=False, action='store_true')
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
        if args.json:
            print(song.json(), end='')
        else:
            print(song, end='')
    elif args.command == 'get-playlist':
        playlist = controls.get_playlist(auth_token, args.context_uri)
        print(playlist, end='')
    elif args.command == 'queue-song':
        resp = controls.queue_track(auth_token, args.context_uri)
        if resp.status_code >= 400:
            print_if_debug(resp.json())
        print_if_debug(resp.status_code)
    elif args.command == 'search':
        resp = controls.search_song(auth_token, args.query)
        for song in resp:
            print(f'{str(song)}###{repr(song)}')
    elif args.command == 'get-playlists':
        LOCAL = 'local_playlists'
        if not args.no_cache:
            if res := get_with_ttl(LOCAL, ttl_seconds=60*60):
                print(res)
                exit()

        playlists = controls.get_playlists(auth_token)
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for playlist in playlists:
                futures.append(
                    executor.submit(lambda p: controls.populate_playlist_tracks(auth_token, p), playlist)
                )

            for f in futures:
                f.result()

        s = []
        for playlist in playlists:
            s.append(playlist.serialize())

        contents = '\n'.join(s)
        write(LOCAL, contents)
        print(contents)
    elif args.command == 'get-recommendations':
        recs = controls.get_recommendations(auth_token, context_uri=args.context_uri)
        for song in recs:
            print(song)
    elif args.command == 'get-queue':
        songs = controls.get_queue(auth_token)
        for song in songs:
            print(song)
    elif args.command == 'get-featured-playlists':
        LOCAL = 'featured_playlists'
        if not args.no_cache:
            if res := get_with_ttl(LOCAL, ttl_seconds=60*60):
                print(res)
                exit()

        playlists = controls.get_featured_playlists(auth_token)

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for playlist in playlists:
                futures.append(
                    executor.submit(lambda p: controls.populate_playlist_tracks(auth_token, p), playlist)
                )

            for f in futures:
                f.result()

        s = []
        for p in playlists:
            s.append(p.serialize())

        contents = '\n'.join(s)
        write(LOCAL, contents)
        print(contents)
    elif args.command == 'add-tracks':
        success = controls.save_tracks(auth_token, args.tracks)
        if not success:
            exit(1)
    elif args.command == 'delete-tracks':
        success = controls.remove_saved_tracks(auth_token, args.tracks)
        if not success:
            exit(1)
    else:
        exit(1)

