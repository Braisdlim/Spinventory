import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-segura'
    SIROPE_DIR = 'data'