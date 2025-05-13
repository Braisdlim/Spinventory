import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-muy-segura'
    SIROPE_DIR = 'data'  # Directorio para almacenamiento local
    # No necesitas configurar redis_url en esta versión