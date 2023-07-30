
class Song:
    def __init__(self, name, artists, album):
        self.name = name
        self.artists = artists
        self.album = album


    def __str__(self):
        artists = ', '.join(self.artists)
        return f"{self.name} - {artists}"
