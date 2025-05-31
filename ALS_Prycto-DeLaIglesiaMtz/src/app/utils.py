import hashlib
import os
import redis
import pickle
from config import Config
from app.records.models import Review
from flask import current_app

def allowed_file(filename):
    """
    Comprueba si el archivo tiene una extensión permitida para imágenes.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def save_unique_image(file_bytes, original_filename, upload_folder):
    """
    Guarda una imagen en el sistema de archivos solo si no existe ya una igual (por hash).
    Devuelve el nombre de archivo único.
    """
    img_hash = hashlib.sha256(file_bytes).hexdigest()
    ext = os.path.splitext(original_filename)[1].lower()
    filename = f"{img_hash}{ext}"
    filepath = os.path.join(upload_folder, filename)
    # Si ya existe, no lo vuelvas a guardar
    if not os.path.exists(filepath):
        with open(filepath, "wb") as f:
            f.write(file_bytes)
    return filename

def get_redis_conn():
    """
    Devuelve una conexión a la base de datos Redis usando la configuración global.
    """
    return redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        decode_responses=False,
    )

def save_wish(wish):
    """
    Guarda un objeto WishRecord en Redis.
    """
    r = get_redis_conn()
    key = f"wish:{wish._id}"
    r.set(key, pickle.dumps(wish))

def load_all_wishes(user_email=None):
    """
    Carga todos los deseos (WishRecord) de Redis.
    Si se proporciona user_email, filtra solo los de ese usuario.
    """
    r = get_redis_conn()
    wishes = []
    for key in r.scan_iter("wish:*"):
        wish = pickle.loads(r.get(key))
        if user_email is None or wish.user_email == user_email:
            wishes.append(wish)
    return wishes

def delete_wish_by_id(wish_id):
    """
    Elimina un deseo (WishRecord) de Redis por su ID.
    """
    r = get_redis_conn()
    key = f"wish:{wish_id}"
    return r.delete(key)

def save_record(record):
    """
    Guarda un objeto Record en Redis.
    """
    r = get_redis_conn()
    key = f"record:{record.id}"
    r.set(key, pickle.dumps(record))

def load_all_records(user_email=None):
    """
    Carga todos los discos (Record) de Redis.
    Si se proporciona user_email, filtra solo los de ese usuario.
    """
    r = get_redis_conn()
    records = []
    for key in r.scan_iter("record:*"):
        record = pickle.loads(r.get(key))
        if user_email is None or record.user_email == user_email:
            records.append(record)
    return records

def delete_record_by_id(record_id):
    """
    Elimina un disco (Record) de Redis por su ID.
    """
    r = get_redis_conn()
    key = f"record:{record_id}"
    return r.delete(key)

def delete_review_by_id(review_id):
    """
    Elimina una reseña (Review) de Redis por su ID.
    """
    r = get_redis_conn()
    key = f"review:{review_id}"
    return r.delete(key)

def save_review(review):
    """
    Guarda un objeto Review en Redis.
    """
    r = get_redis_conn()
    key = f"review:{review._id}"
    r.set(key, pickle.dumps(review))

def load_all_reviews(record_id=None):
    """
    Carga todas las reseñas (Review) de Redis.
    Si se proporciona record_id, filtra solo las de ese disco.
    """
    r = get_redis_conn()
    reviews = []
    for key in r.scan_iter("review:*"):
        review = pickle.loads(r.get(key))
        if record_id is None or review.record_id == record_id:
            reviews.append(review)
    return reviews

def safe_delete_cover(portada_filename):
    """
    Elimina la imagen de portada del sistema de archivos solo si ningún otro disco o deseo la está usando.
    """
    if not portada_filename:
        return
    # Busca en todos los records y wishes si alguien más usa esa portada
    for record in load_all_records():
        if record.portada_filename == portada_filename:
            return  # Alguien más la usa, no borrar
    for wish in load_all_wishes():
        if wish.portada_filename == portada_filename:
            return  # Alguien más la usa, no borrar
    # Si llegamos aquí, nadie la usa, podemos borrar
    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], portada_filename)
    if os.path.exists(image_path):
        os.remove(image_path)