from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from mongoengine import Document, StringField, DateTimeField, BooleanField, IntField, SequenceField
from mongoengine import connect
from flask_login import UserMixin


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
      




