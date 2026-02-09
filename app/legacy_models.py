from . import DB
from flask_login import UserMixin
from datetime import datetime

class LegacyCelebrity(DB.Model):
    __tablename__ = 'celebrity'
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

class LegacyUser(UserMixin, DB.Model):
    __tablename__ = 'user'
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(80), unique=True, nullable=False)
    password_hash = DB.Column(DB.String(200), nullable=False)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class LegacyCelebritySubmission(DB.Model):
    __tablename__ = 'celebrity_submission'
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(120), nullable=False)
    email = DB.Column(DB.String(120), nullable=False)
    phone = DB.Column(DB.String(60), nullable=False)
    category = DB.Column(DB.String(120))
    bio = DB.Column(DB.Text)
    youtube = DB.Column(DB.String(255))
    tiktok = DB.Column(DB.String(255))
    spotify = DB.Column(DB.String(255))
    photo_filename = DB.Column(DB.String(255))
    status = DB.Column(DB.String(20), default="pending")
    created_at = DB.Column(DB.DateTime, default=datetime.utcnow)

class LegacyOnboardingRegistration(DB.Model):
    __tablename__ = 'onboarding_registration'
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(120), nullable=False)
    email = DB.Column(DB.String(120), nullable=False)
    phone = DB.Column(DB.String(50), nullable=False)
    message = DB.Column(DB.Text)
    status = DB.Column(DB.String(20), default="pending")
    created_at = DB.Column(DB.DateTime, default=datetime.utcnow)
