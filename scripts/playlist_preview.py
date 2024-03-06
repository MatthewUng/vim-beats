# On input the serialized version of a playlist from stdin
# returns the preview to stdout

p = input()
v = p.split('###')
name = v[0]
owner = v[1]
playlist_id = v[2]
description = v[3]

songs = [] if len(v) <= 4 else v[4:]

print(f"""{name}
by {owner}

{description}""")

if songs:
    print()
    for song in songs:
        print(song)
