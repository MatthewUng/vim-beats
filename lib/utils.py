
def get_playlist_id(context_uri):
    """Obtains the playlist_id from a context_uri"""

    prefix = "spotify:playlist:"
    if len(context_uri) < len(prefix) or context_uri[:len(prefix)] != prefix:
        return ''
    return context_uri[len(prefix):]
