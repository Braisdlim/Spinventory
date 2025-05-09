from flask import Flask
from sirope import Sirope
from flask_login import LoginManager

# Configuración correcta para Sirope + Redis
srp = Sirope()  # Así usa Redis en localhost:6379 por defecto

# Si necesitas configurar Redis explícitamente, hazlo ANTES de crear Sirope:
import redis
redis_conn = redis.Redis(host="127.0.0.1", port=6379)
srp = Sirope(redis_conn)  # Pasa la conexión Redis ya configurada

app = Flask(__name__)
app.secret_key = "tu_clave_secreta"  # Cambia esto en producción
lm = LoginManager(app)
srp = Sirope()

# Importar blueprints
from routes.auth import auth_bp
from routes.records import records_bp
app.register_blueprint(auth_bp)
app.register_blueprint(records_bp)

from models.user import User

@lm.user_loader
def load_user(user_id):
    return User.find(srp, user_id)

if __name__ == "__main__":
    app.run(debug=True)