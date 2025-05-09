import uuid
from sirope import OID

class VinylRecord:
    def __init__(self, user_id, title, artist, year, cover_url=""):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.artist = artist
        self.year = year
        self.cover_url = cover_url

    @staticmethod
    def find(srp, record_id):
        return srp.find_first(VinylRecord, lambda r: r.id == record_id)