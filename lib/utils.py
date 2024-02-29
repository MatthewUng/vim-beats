from lib.api import SpotifyObj

def get_playlist_id(context_uri):
    """Obtains the playlist_id from a context_uri"""

    prefix = "spotify:playlist:"
    if len(context_uri) < len(prefix) or context_uri[:len(prefix)] != prefix:
        return ''
    return context_uri[len(prefix):]

def get_track_id(context_uri):
    prefix = "spotify:track:"
    if len(context_uri) < len(prefix) or context_uri[:len(prefix)] != prefix:
        return ''
    return context_uri[len(prefix):]

def get_artist_id(context_uri):
    prefix = "spotify:artist:"
    if len(context_uri) < len(prefix) or context_uri[:len(prefix)] != prefix:
        return ''
    return context_uri[len(prefix):]

def context_uri_to_obj_type(s):
    track = "spotify:track:"
    playlist = "spotify:playlist:"
    artist = "spotify:artist:"
    if s.startswith(track):
        return SpotifyObj.TRACK
    if s.startswith(playlist):
        return SpotifyObj.PLAYLIST
    if s.startswith(artist):
        return SpotifyObj.ARTIST
