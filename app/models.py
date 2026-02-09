import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Determine which database mode to use
USE_MONGO = bool(os.getenv('MONGO_URI'))

if USE_MONGO:
    # MongoDB mode (production on Render)
    from mongoengine import Document, StringField, DateTimeField, BooleanField, IntField, SequenceField
    
    class Celebrity(Document):
        meta = {'collection': 'celebrities'}
        id = SequenceField(primary_key=True)
        name = StringField(max_length=140, required=True)
        slug = StringField(max_length=160, required=True, unique=True)
        bio = StringField()
        category = StringField(max_length=80)
        photo_filename = StringField(max_length=300)
        youtube = StringField(max_length=300)
        tiktok = StringField(max_length=300)
        spotify = StringField(max_length=300)
        featured = BooleanField(default=False)
        created_at = DateTimeField(default=datetime.utcnow)

        @property
        def photo_url(self):
            if self.photo_filename:
                return f"/static/uploads/{self.photo_filename}"
            return None

    class User(UserMixin, Document):
        meta = {'collection': 'users'}
        id = SequenceField(primary_key=True)
        username = StringField(max_length=80, required=True, unique=True)
        password_hash = StringField(max_length=200, required=True)

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

    class CelebritySubmission(Document):
        meta = {'collection': 'celebrity_submissions'}
        id = SequenceField(primary_key=True)
        name = StringField(max_length=120, required=True)
        email = StringField(max_length=120, required=True)
        phone = StringField(max_length=60, required=True)
        category = StringField(max_length=120)
        bio = StringField()
        youtube = StringField(max_length=255)
        tiktok = StringField(max_length=255)
        spotify = StringField(max_length=255)
        photo_filename = StringField(max_length=255)
        status = StringField(max_length=20, default="pending")
        created_at = DateTimeField(default=datetime.utcnow)

    class OnboardingRegistration(Document):
        meta = {'collection': 'onboarding_registrations'}
        id = SequenceField(primary_key=True)
        name = StringField(max_length=120, required=True)
        email = StringField(max_length=120, required=True)
        phone = StringField(max_length=50, required=True)
        message = StringField()
        status = StringField(max_length=20, default="pending")
        created_at = DateTimeField(default=datetime.utcnow)

else:
    # SQLAlchemy mode (local development)
    from . import DB
    
    class Celebrity(DB.Model):
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

        @property
        def photo_url(self):
            if self.photo_filename:
                return f"/static/uploads/{self.photo_filename}"
            return None

    class User(UserMixin, DB.Model):
        __tablename__ = 'user'
        id = DB.Column(DB.Integer, primary_key=True)
        username = DB.Column(DB.String(80), unique=True, nullable=False)
        password_hash = DB.Column(DB.String(200), nullable=False)

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

    class CelebritySubmission(DB.Model):
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

    class OnboardingRegistration(DB.Model):
        __tablename__ = 'onboarding_registration'
        id = DB.Column(DB.Integer, primary_key=True)
        name = DB.Column(DB.String(120), nullable=False)
        email = DB.Column(DB.String(120), nullable=False)
        phone = DB.Column(DB.String(50), nullable=False)
        message = DB.Column(DB.Text)
        status = DB.Column(DB.String(20), default="pending")
        created_at = DB.Column(DB.DateTime, default=datetime.utcnow)
      




