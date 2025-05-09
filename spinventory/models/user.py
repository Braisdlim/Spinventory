from flask_login import UserMixin
from sirope import Sirope
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, email, password):
        self.id = email
        self.password = generate_password_hash(password)
        self.vinyls = []  # Esta lista almacenará OIDs de discos

    @staticmethod
    def find(srp, email):
        return srp.find_first(User, lambda u: u.id == email)

    def check_password(self, password):
        return check_password_hash(self.password, password)