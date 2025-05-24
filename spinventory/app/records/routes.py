from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.records.models import Record, WishRecord, Review, Genre  # Asegúrate de importar Review
from app.records.models import User
from app.utils import (
    save_record, load_all_records, delete_record_by_id,
    save_wish, load_all_wishes, delete_review_by_id,
    save_review, load_all_reviews, get_redis_conn, delete_wish_by_id,
    safe_delete_cover
)
import os
import uuid
from datetime import datetime
import requests
from config import Config
from app.utils import save_unique_image
from app import srp  # Import srp for storage/repository provider

# Definición del Blueprint
records_bp = Blueprint('records', __name__)


@records_bp.route('/')
def index():
    return render_template('index.html', now=datetime.now)

@records_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            # Validación básica de campos requeridos
            required_fields = ['title', 'artist', 'year', 'genre', 'condition']
            if not all(request.form.get(field) for field in required_fields):
                flash('Por favor complete todos los campos requeridos', 'error')
                return render_template('records/add.html')
            
            # Procesar el género (desplegable o personalizado)
            genre_name = request.form.get('genre')
            if genre_name == "Otro...":
                genre_name = request.form.get('other_genre', '').strip()
            genre = Genre(name=genre_name)
            
            # Procesar la imagen de portada
            portada_filename = None
            if 'cover' in request.files:
                cover_file = request.files['cover']
                if cover_file.filename != '':
                    if not allowed_file(cover_file.filename):
                        flash('Formato de imagen no válido. Use JPG, PNG o GIF.', 'error')
                        return render_template('records/add.html')
                    
                    file_bytes = cover_file.read()
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    portada_filename = save_unique_image(file_bytes, cover_file.filename, current_app.config['UPLOAD_FOLDER'])

            # Procesar etiquetas correctamente
            tags_raw = request.form.get('tags', '')
            tags = [t.strip() for t in tags_raw.split(',') if t.strip()]

            # Procesar portada automática si no se subió archivo
            if not portada_filename and request.form.get('auto_cover_url'):
                cover_url = request.form.get('auto_cover_url')
                if cover_url:
                    response = requests.get(cover_url)
                    if response.status_code == 200:
                        ext = cover_url.split('.')[-1].split('?')[0]
                        # Usa el sistema de hash para evitar duplicados
                        portada_filename = save_unique_image(response.content, f"autocover.{ext}", current_app.config['UPLOAD_FOLDER'])

            # Crear el registro del disco
            record = Record(
                title=request.form.get('title').strip(),
                artist=request.form.get('artist').strip(),
                year=int(request.form.get('year')),
                genre=genre,
                condition=request.form.get('condition'),
                user_email=current_user.email,
                portada_filename=portada_filename,
                tags=tags
            )
            
            if not isinstance(record.genre, Genre):
                record.genre = Genre(name=record.genre)
            save_record(record)
            
            flash('Disco añadido correctamente!', 'success')
            return redirect(url_for('records.my_collection'))
            
        except ValueError as ve:
            flash('El año debe ser un número válido', 'error')
            current_app.logger.error(f"ValueError en add: {str(ve)}")
        except Exception as e:
            flash('Error al añadir el disco', 'error')
            current_app.logger.error(f"Add record error: {str(e)}", exc_info=True)
    
    return render_template('records/add.html')

@records_bp.route('/delete/<record_id>', methods=['POST'])
@login_required
def delete(record_id):
    try:
        records = load_all_records(current_user.email)
        for record_obj in records:
            if record_obj.id == record_id and record_obj.user_email == current_user.email:
                # Elimina la imagen de portada si existe
                if record_obj.portada_filename:
                    safe_delete_cover(record_obj.portada_filename)
                print(f"Intentando borrar record con id: {record_obj.id}")
                deleted = delete_record_by_id(record_obj.id)
                if deleted:
                    flash('Disco eliminado correctamente.', 'success')
                else:
                    flash('No se pudo eliminar el disco.', 'error')
                break
        else:
            flash('No se encontró el disco o no tienes permiso para eliminarlo.', 'error')
    except Exception as e:
        flash('Error al eliminar el disco.', 'error')
        current_app.logger.error(f"Error al eliminar disco: {str(e)}", exc_info=True)
    return redirect(url_for('records.my_collection'))

@records_bp.route('/wishlist', methods=['GET'])
@login_required
def wishlist():
    wish_records = load_all_wishes(current_user.email)
    return render_template('records/wishlist.html', wish_records=wish_records)

@records_bp.route('/wishlist/add', methods=['GET', 'POST'])
@login_required
def add_wish():
    if request.method == 'POST':
        portada_filename = None

        # Si el usuario sube una imagen
        if 'cover' in request.files:
            cover_file = request.files['cover']
            if cover_file and cover_file.filename != '' and allowed_file(cover_file.filename):
                file_bytes = cover_file.read()
                portada_filename = save_unique_image(file_bytes, cover_file.filename, current_app.config['UPLOAD_FOLDER'])

        # Si se usa una URL de portada automática
        if not portada_filename and request.form.get('auto_cover_url'):
            cover_url = request.form.get('auto_cover_url')
            if cover_url:
                response = requests.get(cover_url)
                if response.status_code == 200:
                    ext = cover_url.split('.')[-1].split('?')[0]
                    portada_filename = save_unique_image(response.content, f"autocover.{ext}", current_app.config['UPLOAD_FOLDER'])

        # Procesar el género (desplegable o personalizado)
        genre_name = request.form.get('genre')
        if genre_name == "Otro...":
            genre_name = request.form.get('other_genre', '').strip()
        genre = Genre(name=genre_name)

        wish = WishRecord(
            title=request.form.get('title').strip(),
            artist=request.form.get('artist').strip(),
            year=int(request.form.get('year')),
            genre=genre,
            user_email=current_user.email,
            portada_filename=portada_filename
        )
        if not isinstance(wish.genre, Genre):
            wish.genre = Genre(name=wish.genre)
        save_wish(wish)
        flash('Disco añadido a la WishList!', 'success')
        return redirect(url_for('records.wishlist'))
    return render_template('records/add_wish.html')

@records_bp.route('/wishlist/delete/<wish_id>', methods=['POST'])
@login_required
def delete_wish(wish_id):
    wishes = load_all_wishes(current_user.email)
    wish = next((w for w in wishes if w._id == wish_id), None)
    if wish:
        # Elimina la imagen de portada si existe
        if wish.portada_filename:
            safe_delete_cover(wish.portada_filename)
        print(f"Intentando borrar clave: wish:{wish._id}")
        # DEBUG: imprime todas las claves de wishlist
        r = get_redis_conn()
        print("Claves wishlist en Redis:", list(r.scan_iter("wish:*")))
        deleted = delete_wish_by_id(wish._id)
        print("Resultado delete:", deleted)
        if deleted:
            flash('Disco eliminado de la WishList.', 'success')
        else:
            flash('No se pudo eliminar el disco de la WishList.', 'error')
    else:
        flash('No se encontró el disco en la WishList.', 'error')
    return redirect(url_for('records.wishlist'))

@records_bp.route('/wishlist/move/<wish_id>', methods=['GET', 'POST'])
@login_required
def move_to_collection_form(wish_id):
    from app.utils import delete_wish_by_id
    wishes = load_all_wishes(current_user.email)
    wish = next((w for w in wishes if w._id == wish_id), None)
    if not wish:
        flash('No se encontró el disco en la WishList.', 'error')
        return redirect(url_for('records.wishlist'))

    if request.method == 'POST':
        condition = request.form.get('condition')
        record = Record(
            title=wish.title,
            artist=wish.artist,
            year=wish.year,
            genre=wish.genre,
            condition=condition,
            user_email=wish.user_email,
            portada_filename=wish.portada_filename
        )
        if not isinstance(record.genre, Genre):
            record.genre = Genre(name=record.genre)
        save_record(record)
        delete_wish_by_id(wish._id)  # <--- Elimina de la wishlist automáticamente
        flash('Disco movido a tu colección.', 'success')
        return redirect(url_for('records.my_collection'))

    return render_template('records/move_to_collection.html', wish=wish)

@records_bp.route('/edit/<record_id>', methods=['GET', 'POST'])
@login_required
def edit(record_id):
    # Busca el disco del usuario actual
    record = next((r for r in load_all_records() if getattr(r, '_id', None) == record_id), None)
    if not record:
        flash('Disco no encontrado o no tienes permiso para editarlo.', 'error')
        return redirect(url_for('records.my_collection'))

    if request.method == 'POST':
        record.title = request.form.get('title').strip()
        record.artist = request.form.get('artist').strip()
        record.year = int(request.form.get('year'))
        genre_name = request.form.get('genre')
        if genre_name == "Otro...":
            genre_name = request.form.get('other_genre', '').strip()
        record.genre = Genre(name=genre_name)  # SIEMPRE objeto Genre

        record.condition = request.form.get('condition')
        tags_raw = request.form.get('tags', '')
        record.tags = [t.strip() for t in tags_raw.split(',') if t.strip()]

        # Si se sube una nueva portada, la reemplaza
        if 'cover' in request.files:
            file = request.files['cover']
            if file and allowed_file(file.filename):
                filename = secure_filename(str(uuid.uuid4()).replace("-", "") + "_" + file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                # Borra la portada anterior si existe
                if record.portada_filename:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], record.portada_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                record.portada_filename = filename
        save_record(record)
        flash('Disco editado correctamente.', 'success')
        return redirect(url_for('records.my_collection'))

    # Prepara las etiquetas como texto para el input
    tags_str = ', '.join(record.tags) if hasattr(record, 'tags') else ''
    # Obtén solo el nombre del género para el select
    genre_name = record.genre.name if hasattr(record.genre, 'name') else str(record.genre)
    # Lista de géneros predefinidos (ajusta según tu app)
    genres = ["Rock", "Pop", "Jazz", "Clásica", "Hip-Hop", "Electrónica", "Otro..."]

    return render_template(
        'records/edit.html',
        record=record,
        tags_str=tags_str,
        genre_name=genre_name,
        genres=genres
    )

@records_bp.route('/api/cover', methods=['GET'])
@login_required
def get_album_cover():
    artist = request.args.get('artist')
    album = request.args.get('title')
    if not artist or not album:
        print("Faltan parámetros")
        return jsonify({"cover_url": None})

    api_key = current_app.config["LASTFM_API_KEY"]
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "album.getinfo",
        "api_key": api_key,
        "artist": artist,
        "album": album,
        "format": "json"
    }
    resp = requests.get(url, params=params)
    print("Last.fm URL:", resp.url)
    data = resp.json()
    print("Last.fm response:", data)
    image_url = None

    # Busca primero 'extralarge' o 'mega', luego cualquier otra disponible
    if "album" in data and "image" in data["album"]:
        images = data["album"]["image"]
        # Busca 'extralarge' o 'mega'
        for img in images:
            if img.get("size") in ("extralarge", "mega") and img.get("#text"):
                image_url = img["#text"]
                break
        # Si no encontró, busca cualquier imagen disponible
        if not image_url:
            for img in images:
                if img.get("#text"):
                    image_url = img["#text"]
                    break

    print("Devuelvo:", image_url)
    return jsonify({"cover_url": image_url})

@records_bp.route('/record/<record_id>', methods=['GET', 'POST'])
@login_required
def record_detail(record_id):
    record = next((r for r in load_all_records() if getattr(r, '_id', None) == record_id), None)
    if not record:
        flash('Disco no encontrado.', 'error')
        return redirect(url_for('records.my_collection'))

    if request.method == 'POST':
        comment = request.form.get('comment', '').strip()
        stars = int(request.form.get('stars', 0))
        # Solo una review por usuario, título y artista
        existing = [
            rv for rv in load_all_reviews()
            if rv.user_email == current_user.email and
               rv.title.lower() == record.title.lower() and
               rv.artist.lower() == record.artist.lower()
        ]
        if not existing:
            review = Review(
                record_id=record._id,
                user_email=current_user.email,
                comment=comment,
                stars=stars,
                title=record.title,
                artist=record.artist
            )
            save_review(review)
            flash('¡Review añadida!', 'success')
        else:
            flash('Ya has valorado este disco.', 'warning')
        return redirect(url_for('records.record_detail', record_id=record_id))

    # Mostrar todas las reviews para discos con mismo título y artista
    reviews = [
        rv for rv in load_all_reviews()
        if rv.title.lower() == record.title.lower() and
           rv.artist.lower() == record.artist.lower()
    ]
    avg_stars = round(sum(rv.stars for rv in reviews) / len(reviews), 2) if reviews else None

    # Cargar usuarios para mostrar el nombre en las reviews
    users = list(srp.load_all(User))
    users_by_email = {u.email: u for u in users}

    return render_template(
        'records/record_detail.html',
        record=record,
        reviews=reviews,
        avg_stars=avg_stars,
        users_by_email=users_by_email
    )

@records_bp.route('/review/<review_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = next((rv for rv in load_all_reviews() if rv._id == review_id), None)
    if not review or review.user_email != current_user.email:
        abort(403)
    if request.method == 'POST':
        review.comment = request.form.get('comment', '').strip()
        review.stars = int(request.form.get('stars', 0))
        save_review(review)
        flash('Review editada correctamente.', 'success')
        return redirect(url_for('records.record_detail', record_id=review.record_id))
    return render_template('records/edit_review.html', review=review)

@records_bp.route('/review/<review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    review = next((rv for rv in load_all_reviews() if rv._id == review_id and rv.user_email == current_user.email), None)
    if review:
        delete_review_by_id(review_id)
        flash('Review eliminada correctamente.', 'success')
        return redirect(url_for('records.record_detail', record_id=review.record_id))
    abort(403)

@records_bp.route('/users')
@login_required
def users():
    users = [u for u in srp.load_all(User) if u.email != current_user.email]
    return render_template('records/users.html', users=users)

@records_bp.route('/user/<user_email>')
@login_required
def user_collection(user_email):
    records = load_all_records(user_email)
    is_own_collection = (user_email == current_user.email)
    # Busca el usuario por email
    user = next((u for u in srp.load_all(User) if u.email == user_email), None)
    username = user.username if user else user_email
    return render_template(
        'records/list.html',
        records=records,
        is_own_collection=is_own_collection,
        user_email=user_email,
        username=username
    )

@records_bp.route('/mycollection')
@login_required
def my_collection():
    records = load_all_records(current_user.email)
    return render_template('records/list.html', records=records, is_own_collection=True, user_email=current_user.email)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']