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
    href = js['href']

    out = Playlist(name, description, owner, id, href)
    try:
        tracks_href = js['tracks']['href']
        out.tracks_href = tracks_href
    except:
        pass

    try:
        total_tracks = js['tracks']['total']
        out.total_tracks = total_tracks
    except:
        pass

    try:
        total_tracks = js['tracks']['total']
        out.total_tracks = total_tracks
    except:
        pass

    try:
        for track in js['tracks']['items']:
            out.tracks.append(json_to_song(track['track']))
    except Exception as e:
        pass

    return out
