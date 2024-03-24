import sys
import json

s = input()
js = json.loads(s)

for track in js:
    print(track['display_name'])
