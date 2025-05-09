from flask import Flask
from flask_login import LoginManager
from sirope import Sirope
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicialización para Sirope 0.3.1 (sin init_app)
    srp = Sirope(app)  # ¡Así se usa en esta versión!
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Hacemos srp disponible globalmente
    app.srp = srp

    # Blueprints (importamos aquí para evitar circulares)
    from app.auth.routes import auth_bp
    from app.records.routes import records_bp
    from app.main.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(main_bp)

    return app