import time
from sirope import OID

class VinylRecord:
    def __init__(self, user_id, title, artist, year):
        self.id = OID(self.__class__.__name__, int(time.time() * 1000))  # Timestamp como entero
        self.user_id = user_id
        self.title = title
        self.artist = artist
        self.year = year
        
    @property
    def id_str(self):
        return str(self.id)