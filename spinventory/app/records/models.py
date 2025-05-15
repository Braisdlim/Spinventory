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

    def to_dict(self):
        """Serialización para Sirope"""
        return {
            '_id': self._id,
            'email': self.email,
            'username': self.username,
            'password': self.password,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialización desde Sirope"""
        return cls(
            email=data['email'],
            username=data['username'],
            password=data['password'],
            id=data.get('_id', data.get('email'))
        )

class Record:  
    def __init__(self, title, artist, year, genre, condition, user_email, portada_filename=None, tags=None, id=None):
        self._id = id or str(uuid.uuid4())  # Atributo especial para Sirope
        self.title = title
        self.artist = artist
        self.year = year
        self.genre = genre
        self.condition = condition
        self.user_email = user_email
        self.portada_filename = portada_filename
        self.tags = tags or []  # <-- Añade este campo
        self.created_at = datetime.now().isoformat()

    @property
    def id(self):
        """Propiedad para compatibilidad con código existente"""
        return self._id

    def to_dict(self):
        """Serialización para Sirope"""
        return {
            '_id': self._id,
            'title': self.title,
            'artist': self.artist,
            'year': self.year,
            'genre': self.genre,
            'condition': self.condition,
            'user_email': self.user_email,
            'portada_filename': self.portada_filename,
            'tags': self.tags,  # <-- Asegúrate de serializar los tags
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialización desde Sirope"""
        record = cls(
            title=data['title'],
            artist=data['artist'],
            year=data['year'],
            genre=data['genre'],
            condition=data['condition'],
            user_email=data['user_email'],
            portada_filename=data.get('portada_filename'),
            id=data.get('_id')
        )
        # Añade esto para compatibilidad con datos antiguos
        record.created_at = data.get('created_at', datetime.now().isoformat())
        return record

    def __eq__(self, other):
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

class WishRecord:
    def __init__(self, title, artist, year, genre, user_email, portada_filename=None, id=None):
        self._id = id or str(uuid.uuid4())
        self.title = title
        self.artist = artist
        self.year = year
        self.genre = genre
        self.user_email = user_email
        self.portada_filename = portada_filename  # <-- Añade este campo
        self.created_at = datetime.now().isoformat()

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