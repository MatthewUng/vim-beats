
class Song:
    def __init__(self, name, artists, album):
        self.name = name
        self.artists = artists
        self.album = album


    def __str__(self):
        artists = ', '.join(self.artists)
        return f"{self.name} - {artists}"


class Playlist:
    def __init__(self, name, description, owner):
        self.name = name
        self.description = description
        self.owner = owner

    def __str__(self):
        return f"{self.name}"
