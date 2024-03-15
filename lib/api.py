from enum import Enum
import json

class SpotifyObj(Enum):
    TRACK = 1
    PLAYLIST = 2
    ARTIST = 3

class Song:
    def __init__(self, name, artists, album, track_id):
        self.name = name
        self.artists = artists
        self.album = album
        self.track_id = track_id

    def spotify_uri(self):
        return f'spotify:track:{self.track_id}'


    def json_dict(self):
        js = {
            'name': self.name,
            'artists': self.artists,
            'display_name': self._display_name(),
            'album': self.album,
            'id': self.track_id
        }
        return js

    def json(self):
        return json.dumps(self.json_dict())

    @staticmethod
    def load_json(js):
        return Song(js['name'], js['artists'], js['album'], js['id'])


    def _display_name(self):
        artists = ', '.join(self.artists)
        return f"{self.name} - {artists}"

    def __str__(self):
        return self._display_name()

    def __repr__(self):
        return self.spotify_uri()


class Playlist:
    def __init__(self, name, description, owner, playlist_id, href):
        # required
        self.name = name
        self.description = description

        self.owner = owner
        self.playlist_id = playlist_id
        self.href = href

        # optional
        self.tracks_href = None
        self.total_tracks = None
        self.tracks = []

    def spotify_uri(self):
        return f'spotify:playlist:{self.playlist_id}'

    def _display_name(self):
        return f'{self.name} ~ {self.owner}'

    def json_dict(self):
        js = {
            'name': self.name,
            'display_name': self._display_name(),
            'description': self.description,
            'owner': self.owner,
            'id': self.playlist_id,
            'href': self.href,
            'tracks': []
        }
        for track in self.tracks:
            js['tracks'].append(track.json_dict())
        return js

    def json(self):
        return json.dumps(self.json_dict())

    @staticmethod
    def load_json(js):
        p = Playlist(js['name'], js['description'], js['owner'], js['id'], js['href'])
        for track in js.get('track', []):
            p.tracks.append(Song.load_json(track))

        return p


    # pass information about playlist in a single line to be used by other applications
    def serialize(self):
        s = [
                self.name,
                self.owner,
                self.playlist_id,
                self.description,
            ]

        for track in self.tracks:
            s.append(str(track))
        return '###'.join(s)

    def __str__(self):
        return f"{self.name} - {self.owner}"

    def __repr__(self):
        return self.playlist_id
