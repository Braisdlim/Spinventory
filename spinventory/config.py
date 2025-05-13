import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu-clave-secreta-aqui'
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0