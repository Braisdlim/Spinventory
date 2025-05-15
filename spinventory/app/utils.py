import hashlib
import os

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def save_unique_image(file_bytes, original_filename, upload_folder):
    img_hash = hashlib.sha256(file_bytes).hexdigest()
    ext = os.path.splitext(original_filename)[1].lower()
    filename = f"{img_hash}{ext}"
    filepath = os.path.join(upload_folder, filename)
    if not os.path.exists(filepath):
        with open(filepath, "wb") as f:
            f.write(file_bytes)
    return filename