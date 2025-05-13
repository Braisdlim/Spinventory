from flask import Flask, redirect, url_for
from flask_login import LoginManager
from sirope import Sirope
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configuración CORRECTA para Sirope 0.3.1
    srp = Sirope(app)  # Sin parámetros adicionales
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Hacemos srp disponible globalmente
    app.srp = srp

    # Blueprints
    from app.auth.routes import auth_bp
    from app.records.routes import records_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(records_bp)

    # Ruta principal
    @app.route('/')
    def index():
        return redirect(url_for('records.list'))

    # User loader (después de crear srp)
    from app.records.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return srp.find_first(User, lambda u: u.email == user_id)

    return app