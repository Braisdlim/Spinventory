from flask_login import UserMixin
from sirope import OID, Sirope
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, email, password):
        self.id = email
        self.password = generate_password_hash(password)
        self.vinyls = []  # Lista de OIDs

    @staticmethod
    def find(srp, email):
        return srp.find_first(User, lambda u: u.id == email)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def add_vinyl(self, vinyl):
        """Añade un OID válido a la colección"""
        if isinstance(vinyl.id, OID):
            self.vinyls.append(vinyl.id)
        else:
            raise TypeError("Se esperaba un OID")

    def get_vinyls(self, srp):
        """Carga segura de discos con verificación de OID"""
        valid_vinyls = []
        for oid in self.vinyls:
            if isinstance(oid, OID):  # Verificación crucial
                vinyl = srp.load(oid)
                if vinyl:
                    valid_vinyls.append(vinyl)
        return valid_vinyls