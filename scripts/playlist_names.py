import sys

# On input the serialized version of a playlist from stdin
# returns the preview to stdout

for line in sys.stdin:
    v = line.split('###')
    name = v[0]

    print(name)
