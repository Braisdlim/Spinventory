from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.records.models import Record, WishRecord, Review, delete_review_by_id  # Asegúrate de importar Review
from app import srp, delete_record_by_id, delete_wish_by_id
from app.records.models import User
import os
import uuid
from datetime import datetime
import redis
import pickle
from config import Config
import requests

# Definición del Blueprint
records_bp = Blueprint('records', __name__)


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
            
            # Procesar la imagen de portada
            portada_filename = None
            if 'cover' in request.files:
                cover_file = request.files['cover']
                if cover_file.filename != '':
                    if not allowed_file(cover_file.filename):
                        flash('Formato de imagen no válido. Use JPG, PNG o GIF.', 'error')
                        return render_template('records/add.html')
                    
                    # Generar nombre único para el archivo
                    ext = cover_file.filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{uuid.uuid4().hex}.{ext}"
                    secure_name = secure_filename(unique_filename)
                    
                    # Asegurar que el directorio existe
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    # Guardar el archivo
                    cover_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_name)
                    cover_file.save(cover_path)
                    portada_filename = secure_name

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
                        filename = secure_filename(f"{uuid.uuid4().hex}_autocover.{ext}")
                        cover_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        with open(cover_path, 'wb') as f:
                            f.write(response.content)
                        portada_filename = filename

            # Crear el registro del disco
            record = Record(
                title=request.form.get('title').strip(),
                artist=request.form.get('artist').strip(),
                year=int(request.form.get('year')),
                genre=request.form.get('genre'),
                condition=request.form.get('condition'),
                user_email=current_user.email,
                portada_filename=portada_filename,
                tags=tags
            )
            
            # Guardar en Sirope - ahora pasamos el objeto directamente
            srp.save(record)
            
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
        for record_obj in srp.load_all(Record):
            if not isinstance(record_obj, Record):
                continue
            if record_obj.id == record_id and record_obj.user_email == current_user.email:
                # Elimina la imagen de portada si existe
                if record_obj.portada_filename:
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], record_obj.portada_filename)
                    if os.path.exists(image_path):
                        os.remove(image_path)
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
    wish_records = [wr for wr in srp.load_all(WishRecord) if wr.user_email == current_user.email]
    return render_template('records/wishlist.html', wish_records=wish_records)

@records_bp.route('/wishlist/add', methods=['GET', 'POST'])
@login_required
def add_wish():
    if request.method == 'POST':
        # ...otros campos...
        portada_filename = None

        # Procesar portada automática si no se subió archivo
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

        wish = WishRecord(
            title=request.form.get('title').strip(),
            artist=request.form.get('artist').strip(),
            year=int(request.form.get('year')),
            genre=request.form.get('genre'),
            user_email=current_user.email,
            portada_filename=portada_filename
        )
        srp.save(wish)
        flash('Disco añadido a la WishList!', 'success')
        return redirect(url_for('records.wishlist'))
    return render_template('records/add_wish.html')

@records_bp.route('/wishlist/delete/<wish_id>', methods=['POST'])
@login_required
def delete_wish(wish_id):
    for wish in srp.load_all(WishRecord):
        if wish._id == wish_id and wish.user_email == current_user.email:
            # Elimina la imagen de portada si existe
            if wish.portada_filename:
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], wish.portada_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
            deleted = delete_wish_by_id(wish._id)
            if deleted:
                flash('Disco eliminado de la WishList.', 'success')
            else:
                flash('No se pudo eliminar el disco de la WishList.', 'error')
            break
    else:
        flash('No se encontró el disco en la WishList.', 'error')
    return redirect(url_for('records.wishlist'))

@records_bp.route('/wishlist/move/<wish_id>', methods=['GET', 'POST'])
@login_required
def move_to_collection_form(wish_id):
    from app import delete_wish_by_id
    wish = next((w for w in srp.load_all(WishRecord) if w._id == wish_id and w.user_email == current_user.email), None)
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
        srp.save(record)
        delete_wish_by_id(wish._id)
        flash('Disco movido a tu colección.', 'success')
        return redirect(url_for('records.my_collection'))

    return render_template('records/move_to_collection.html', wish=wish)

@records_bp.route('/edit/<record_id>', methods=['GET', 'POST'])
@login_required
def edit(record_id):
    # Busca el disco del usuario actual
    record = next((r for r in srp.load_all(Record) if (getattr(r, 'id', None) == record_id or getattr(r, '_id', None) == record_id) and r.user_email == current_user.email), None)
    if not record:
        flash('Disco no encontrado o no tienes permiso para editarlo.', 'error')
        return redirect(url_for('records.my_collection'))

    if request.method == 'POST':
        record.title = request.form.get('title').strip()
        record.artist = request.form.get('artist').strip()
        record.year = int(request.form.get('year'))
        record.genre = request.form.get('genre')
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

        srp.save(record)
        flash('Disco editado correctamente.', 'success')
        return redirect(url_for('records.my_collection'))

    # Prepara las etiquetas como texto para el input
    tags_str = ', '.join(record.tags) if hasattr(record, 'tags') else ''
    return render_template('records/edit.html', record=record, tags_str=tags_str)

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
    # Busca la imagen de mayor tamaño disponible
    if "album" in data and "image" in data["album"]:
        images = data["album"]["image"]
        for img in reversed(images):
            if img["#text"]:
                image_url = img["#text"]
                break
    print("Devuelvo:", image_url)
    return jsonify({"cover_url": image_url})

@records_bp.route('/record/<record_id>', methods=['GET', 'POST'])
@login_required
def record_detail(record_id):
    record = next((r for r in srp.load_all(Record) if r._id == record_id), None)
    if not record:
        flash('Disco no encontrado.', 'error')
        return redirect(url_for('records.my_collection'))

    # Permitir dejar reseña aunque seas el dueño
    if request.method == 'POST':
        comment = request.form.get('comment', '').strip()
        stars = int(request.form.get('stars', 0))
        # Solo una review por usuario, título y artista
        existing = [
            rv for rv in srp.load_all(Review)
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
            srp.save(review)
            flash('¡Review añadida!', 'success')
        else:
            flash('Ya has valorado este disco.', 'warning')
        return redirect(url_for('records.record_detail', record_id=record_id))

    # Mostrar todas las reviews para discos con mismo título y artista
    reviews = [
        rv for rv in srp.load_all(Review)
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
    review = next((rv for rv in srp.load_all(Review) if rv._id == review_id), None)
    if not review or review.user_email != current_user.email:
        abort(403)
    if request.method == 'POST':
        review.comment = request.form.get('comment', '').strip()
        review.stars = int(request.form.get('stars', 0))
        srp.save(review)
        flash('Review editada correctamente.', 'success')
        return redirect(url_for('records.record_detail', record_id=review.record_id))
    return render_template('records/edit_review.html', review=review)

def delete_review_by_id(review_id):
    for review in srp.load_all(Review):
        if getattr(review, '_id', None) == review_id:
            srp.delete(review)
            return True
    return False

@records_bp.route('/review/delete/<review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    from app import delete_review_by_id

    for review in srp.load_all(Review):
        if getattr(review, '_id', None) == review_id and review.user_email == current_user.email:
            deleted = delete_review_by_id(review_id)
            if deleted:
                flash("Reseña eliminada.", "success")
                return redirect(request.referrer or url_for('records.record_detail', record_id=review.record_id))
            break
    flash("No se pudo eliminar la reseña.", "error")
    return redirect(request.referrer or url_for('records.my_collection'))

@records_bp.route('/users')
@login_required
def users():
    users = [u for u in srp.load_all(User) if u.email != current_user.email]
    return render_template('records/users.html', users=users)

@records_bp.route('/user/<user_email>')
@login_required
def user_collection(user_email):
    records = [r for r in srp.load_all(Record) if r.user_email == user_email]
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
    records = [r for r in srp.load_all(Record) if r.user_email == current_user.email]
    return render_template('records/list.html', records=records, is_own_collection=True, user_email=current_user.email)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']