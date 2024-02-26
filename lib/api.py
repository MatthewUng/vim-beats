
class Song:
    def __init__(self, name, artists, album, track_id=''):
        self.name = name
        self.artists = artists
        self.album = album
        self.track_id = track_id

    def spotify_uri(self):
        return f'spotify:track:{self.track_id}'

    def __str__(self):
        artists = ', '.join(self.artists)
        return f"{self.name} - {artists}"

    def __repr__(self):
        return self.track_id


class Playlist:
    def __init__(self, name, description, owner, playlist_id):
        self.name = name
        self.description = description
        self.owner = owner
        self.playlist_id = playlist_id

    def spotify_uri(self):
        return f'spotify:playlist:{self.track_id}'

    def __str__(self):
        return f"{self.name} - {self.owner}"

    def __repr__(self):
        return self.playlist_id
