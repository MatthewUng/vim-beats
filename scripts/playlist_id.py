# On input the serialized version of a playlist from stdin
# returns the playlist id

p = input()
v = p.split('###')
id = v[2]

print(id)

