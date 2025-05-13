from flask import Flask, redirect, url_for
from flask_login import LoginManager
from sirope import Sirope
from config import Config
import redis

# Inicialización de extensiones
login_manager = LoginManager()
srp = None  # Se inicializará después con la app

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configuración de Redis
    redis_conn = redis.Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB'],
        decode_responses=False  # Importante para Sirope
    )
    
    # Inicialización de Sirope
    global srp
    srp = Sirope(redis_obj=redis_conn)
    # ... resto de la configuración ...
    # Configuración de Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Registrar blueprints
    from app.auth import auth_bp
    from app.records import records_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(records_bp, url_prefix='/records')

    # Rutas principales
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # User loader (import aquí para evitar imports circulares)
    from app.records.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return srp.find_first(User, lambda u: u.email == user_id)

    return app