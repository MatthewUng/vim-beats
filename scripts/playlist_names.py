import sys
import json

s = input()
js = json.loads(s)

for playlist in js:
    print(playlist['name'])

