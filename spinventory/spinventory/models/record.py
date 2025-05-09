import uuid
from sirope import OID

class VinylRecord:
    def __init__(self, user_id, title, artist, year):
        self.id = OID(self.__class__.__name__, uuid.uuid4().int & (1<<63)-1)
        self.user_id = user_id
        self.title = title
        self.artist = artist
        self.year = year