from flask import Flask, redirect, url_for, current_app, flash
from flask_login import LoginManager
from sirope import Sirope
from config import Config
import redis
import os
import pickle
from werkzeug.utils import secure_filename
import json

# Inicialización de extensiones globales
login_manager = LoginManager()
srp = None  # Se inicializará después con la app

def create_app():
    """
    Crea e inicializa la aplicación Flask, configurando extensiones,
    blueprints, subida de archivos y conexión a Redis.
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configuración para subida de archivos
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB máximo
    
    # Crear directorio de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Configuración de Redis
    redis_conn = redis.Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB'],
        decode_responses=False  # Importante para Sirope
    )
    
    # Inicialización de Sirope (ORM sobre Redis)
    global srp
    srp = Sirope(redis_obj=redis_conn)
    
    # Configuración de Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Registrar blueprints de autenticación y gestión de discos
    from app.auth import auth_bp
    from app.records import records_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(records_bp)  # Sin url_prefix

    # User loader para Flask-Login (evita imports circulares)
    from app.records.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Carga un usuario por su email desde la base de datos."""
        return srp.find_first(User, lambda u: u.email == user_id)

    return app

# Función de utilidad para verificar extensiones de archivo permitidas
def allowed_file(filename):
    """
    Comprueba si el archivo tiene una extensión permitida para imágenes.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def delete_record_by_id(record_id):
    """
    Elimina un disco (Record) de la base de datos Redis por su ID.
    Intenta deserializar con pickle y, si falla, con JSON.
    Devuelve True si se elimina correctamente, False si no se encuentra.
    """
    import redis
    import pickle
    from config import Config

    r = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        decode_responses=False
    )
    hash_name = "app.records.models.Record"
    print(f"Buscando en hash: {hash_name}")
    for key in r.hkeys(hash_name):
        raw = r.hget(hash_name, key)
        # Intenta deserializar con pickle
        try:
            obj = pickle.loads(raw)
            print(f"Comparando con obj.id={getattr(obj, 'id', None)}, obj._id={getattr(obj, '_id', None)}")
            if hasattr(obj, "id") and str(obj.id) == str(record_id):
                r.hdel(hash_name, key)
                print("Eliminado por id (pickle)")
                return True
            elif hasattr(obj, "_id") and str(obj._id) == str(record_id):
                r.hdel(hash_name, key)
                print("Eliminado por _id (pickle)")
                return True
        except Exception as e:
            # Si falla pickle, intenta como JSON
            try:
                data = json.loads(raw.decode())
                print(f"Comparando con data['id']={data.get('id')}, data['_id']={data.get('_id')}")
                if data.get("id") == record_id or data.get("_id") == record_id:
                    r.hdel(hash_name, key)
                    print("Eliminado por id/_id (json)")
                    return True
            except Exception as e2:
                print(f"Error al deserializar como JSON: {e2}")
                continue
    print("No encontrado")
    return False

def delete_wish_by_id(wish_id):
    """
    Elimina un deseo (WishRecord) de la base de datos Redis por su ID.
    Intenta deserializar con pickle y, si falla, con JSON.
    Devuelve True si se elimina correctamente, False si no se encuentra.
    """
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
    hash_name = "app.records.models.WishRecord"  # Hash correcto para deseos
    print(f"Buscando en hash: {hash_name}")
    for key in r.hkeys(hash_name):
        raw = r.hget(hash_name, key)
        try:
            obj = pickle.loads(raw)
            if hasattr(obj, "id") and str(obj.id) == str(wish_id):
                r.hdel(hash_name, key)
                print("Eliminado por id (pickle)")
                return True
            elif hasattr(obj, "_id") and str(obj._id) == str(wish_id):
                r.hdel(hash_name, key)
                print("Eliminado por _id (pickle)")
                return True
        except Exception:
            try:
                data = json.loads(raw.decode())
                print(f"Comparando con data['id']={data.get('id')}, data['_id']={data.get('_id')}")
                if data.get("id") == wish_id or data.get("_id") == wish_id:
                    r.hdel(hash_name, key)
                    print("Eliminado por id/_id (json)")
                    return True
            except Exception:
                continue
    print("No encontrado")
    return False

def delete_review_by_id(review_id):
    """
    Elimina una reseña (Review) de la base de datos Redis por su ID.
    Intenta deserializar con pickle y, si falla, con JSON.
    Devuelve True si se elimina correctamente, False si no se encuentra.
    """
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
        # Intenta deserializar con pickle
        try:
            obj = pickle.loads(raw)
            print(f"Comparando con obj.id={getattr(obj, 'id', None)}, obj._id={getattr(obj, '_id', None)}")
            if hasattr(obj, "id") and str(obj.id) == str(review_id):
                r.hdel(hash_name, key)
                print("Eliminado por id (pickle)")
                return True
            elif hasattr(obj, "_id") and str(obj._id) == str(review_id):
                r.hdel(hash_name, key)
                print("Eliminado por _id (pickle)")
                return True
        except Exception as e:
            # Si falla pickle, intenta como JSON
            try:
                data = json.loads(raw.decode())
                print(f"Comparando con data['id']={data.get('id')}, data['_id']={data.get('_id')}")
                if data.get("id") == review_id or data.get("_id") == review_id:
                    r.hdel(hash_name, key)
                    print("Eliminado por id/_id (json)")
                    return True
            except Exception as e2:
                print(f"Error al deserializar como JSON: {e2}")
                continue
    print("No encontrado")
    return False