from lib.api import Song, Playlist

def json_to_song(js):
    name = js['name']
    artists = [x['name'] for x in js['artists']]
    album = js['album']['name']
    uri = js['uri']
    return Song(name, artists, album)
    
def json_to_playlist(js):
    name = js['name']
    description = js['description'].strip()
    owner = js['owner']['display_name']
    id = js['id']
    return Playlist(name, description, owner, id)

