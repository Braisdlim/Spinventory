from flask_login import UserMixin
from datetime import datetime
import uuid
import redis
import pickle
from config import Config  # Asegúrate de tener la configuración de Redis disponible
import requests
from flask import current_app
from werkzeug.utils import secure_filename
import os

class User(UserMixin):
    def __init__(self, email, username, password, id=None):
        self._id = id or email  # Usamos email como ID por defecto
        self.email = email
        self.username = username
        self.password = password
        self.created_at = datetime.now().isoformat()
    
    def get_id(self):
        return self.email



class Record:  
    def __init__(self, title, artist, genre, year=None, condition=None, user_email=None, portada_filename=None, tags=None, created_at=None, _id=None):
        import uuid
        self._id = _id or str(uuid.uuid4())  # <-- Así siempre tiene valor único
        self.title = title
        self.artist = artist
        self.genre = genre  # Objeto Genre
        self.year = year
        self.condition = condition
        self.user_email = user_email
        self.portada_filename = portada_filename
        self.tags = tags or []
        self.created_at = created_at
        self._force_pickle = uuid.uuid4()  # <-- Añade esta línea

    @property
    def id(self):
        return self._id

    def __eq__(self, other):
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

class WishRecord(object):  # <--- Hereda explícitamente de object
    __sirope_hash__ = "WishRecord_alsdebug_20250524b"
    def __init__(self, title, artist, year, genre, user_email, portada_filename=None, id=None, created_at=None):
        import uuid
        from datetime import datetime
        self._id = id or str(uuid.uuid4())
        self.title = title
        self.artist = artist
        self.year = year
        self.genre = genre
        self.user_email = user_email
        self.portada_filename = portada_filename
        self.created_at = created_at or datetime.now().isoformat()
        self._force_pickle = uuid.uuid4()  # <--- Esto fuerza a Sirope a usar pickle
class Review:
    def __init__(self, record_id, user_email, comment, stars, title, artist, created_at=None, _id=None):
        self._id = _id or str(uuid.uuid4())
        self.record_id = record_id
        self.user_email = user_email
        self.comment = comment
        self.stars = stars
        self.title = title
        self.artist = artist
        self.created_at = created_at or datetime.utcnow().isoformat()

def delete_record_by_id(record_id):
    r = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        decode_responses=False
    )
    hash_name = "Record"
    print(f"Buscando en hash: {hash_name}")
    for key in r.hkeys(hash_name):
        raw = r.hget(hash_name, key)
        try:
            obj = pickle.loads(raw)
            print(f"DEBUG: key={key}, obj.id={getattr(obj, 'id', None)}, obj._id={getattr(obj, '_id', None)}")
            if hasattr(obj, "id") and obj.id == record_id:
                r.hdel(hash_name, key)
                print("Eliminado por id")
                return True
            elif hasattr(obj, "_id") and obj._id == record_id:
                r.hdel(hash_name, key)
                print("Eliminado por _id")
                return True
        except Exception as e:
            print(f"Error al deserializar: {e}")
            continue
    print("No encontrado")
    return False

def handle_portada_filename(portada_filename, request):
    if not portada_filename and request.form.get('auto_cover_url'):
        cover_url = request.form.get('auto_cover_url')
        if cover_url:
            response = requests.get(cover_url)
            if response.status_code == 200:
                ext = cover_url.split('.')[-1].split('?')[0]
                filename = secure_filename(f"{uuid.uuid4().hex}_autocover.{ext}")
                cover_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                with open(cover_path, 'wb') as f:
                    f.write(response.content)
                portada_filename = filename
    return portada_filename

def delete_review_by_id(review_id):
    import redis
    import pickle
    import json
    from config import Config

    r = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        decode_responses=False
    )
    hash_name = "app.records.models.Review"
    print(f"Buscando en hash: {hash_name}")
    for key in r.hkeys(hash_name):
        raw = r.hget(hash_name, key)
        try:
            obj = pickle.loads(raw)
            if hasattr(obj, "_id") and str(obj._id) == str(review_id):
                r.hdel(hash_name, key)
                print("Eliminado por _id (pickle)")
                return True
        except Exception:
            try:
                data = json.loads(raw.decode())
                if data.get("_id") == review_id:
                    r.hdel(hash_name, key)
                    print("Eliminado por _id (json)")
                    return True
            except Exception:
                continue
    print("No encontrado")
    return False

class Genre:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def __getstate__(self):
        return {"name": self.name, "description": self.description}

    def __setstate__(self, state):
        self.name = state.get("name", "")
        self.description = state.get("description", "")

def create_genre_from_request(request):
    genre_name = request.form.get('genre')
    if genre_name == "Otro...":
        genre_name = request.form.get('other_genre', '').strip()
    genre = Genre(name=genre_name)
    return genre