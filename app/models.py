from . import DB
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Celebrity(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(140), nullable=False)
    slug = DB.Column(DB.String(160), unique=True, nullable=False)
    bio = DB.Column(DB.Text)
    category = DB.Column(DB.String(80))
    photo_filename = DB.Column(DB.String(300))
    youtube = DB.Column(DB.String(300))
    tiktok = DB.Column(DB.String(300))
    spotify = DB.Column(DB.String(300))
    featured = DB.Column(DB.Boolean, default=False)
    created_at = DB.Column(DB.DateTime, default=datetime.utcnow)

    @property
    def photo_url(self):
        if self.photo_filename:
            return f"/static/uploads/{self.photo_filename}"
        return None

class User(UserMixin, DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(80), unique=True, nullable=False)
    password_hash = DB.Column(DB.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
