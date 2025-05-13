from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password
    
    def get_id(self):
        return self.email

class Record:
    def __init__(self, title, artist, year, genre, condition, user_email):
        self.title = title
        self.artist = artist
        self.year = year
        self.genre = genre
        self.condition = condition
        self.user_email = user_email
        self.image_url = ""