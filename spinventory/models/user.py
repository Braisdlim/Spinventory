from flask_login import UserMixin
from sirope import OID, Sirope
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, email, password):
        self.id = email
        self.password = generate_password_hash(password)
        self.vinyls = []  # Lista de OIDs (SiropeId)

    @staticmethod
    def find(srp: Sirope, email: str):
        return srp.find_first(User, lambda u: u.id == email)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def add_vinyl(self, oid: OID):
        """Añade un OID válido a la colección"""
        if isinstance(oid, OID):
            self.vinyls.append(oid)
        else:
            raise TypeError("Se esperaba un OID, se recibió: " + str(type(oid)))
    def get_vinyls(self, srp):
        valid_vinyls = []
        for oid in self.vinyls:
            try:
                if hasattr(oid, 'namespace'):  # Verificación clave para OIDs
                    vinyl = srp.load(oid)
                    if vinyl:
                        valid_vinyls.append(vinyl)
            except Exception as e:
                print(f"Error cargando disco {oid}: {e}")
        return valid_vinyls