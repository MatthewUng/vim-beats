# On input the serialized version of a playlist from stdin
# returns the preview to stdout

import sys
import subprocess
import json

playlist_file = sys.argv[1]
playlist_name = sys.argv[2]

with open(playlist_file) as f:
    js = json.load(f)

for playlist in js:
    if playlist['name'] == playlist_name:

        id = playlist['id']
        cmd = f'python3 ./script.py get-playlist -c \'spotify:playlist:{id}\' --json'
        process = subprocess.run([cmd], capture_output=True, shell=True)

        decoded = process.stdout.decode('utf-8')
        playlist_details = json.loads(decoded)

        owner = playlist['owner']
        desc = playlist['description']

        print(playlist_name)
        print()
        print(f'by {owner}')
        print()
        print(desc)
        print()

        for song in playlist_details.get('tracks', []):
            print(song['display_name'])
        exit()
