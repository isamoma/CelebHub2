import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from mongoengine import Document, StringField, DateTimeField, BooleanField, IntField, SequenceField
from flask_login import UserMixin

# Export the flag used by routes.py
USE_MONGO = True  # models.py is MongoEngine-only


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
    # Payment / feature tracking
    feature_amount = IntField(default=0)  # amount paid (in KES)
    feature_status = StringField(max_length=20, default="none")  # none | pending | paid | failed
    feature_payment_id = StringField(max_length=200)  # payment / transaction id from MPESA
    featured_until = DateTimeField(required=False)
    created_at = DateTimeField(default=datetime.utcnow)

    @property
    def photo_url(self):
        if self.photo_filename:
            return f"/static/uploads/{self.photo_filename}"
        return None

    def mark_featured(self, days=30, payment_id=None, amount=0):
        """Helper to mark a celebrity as featured for `days` days and record payment info."""
        from datetime import timedelta
        self.featured = True
        self.feature_amount = amount
        self.feature_status = 'paid'
        self.feature_payment_id = payment_id
        self.featured_until = datetime.utcnow() + timedelta(days=days)
        self.save()


class User(UserMixin, Document):
    meta = {'collection': 'users'}
    id = SequenceField(primary_key=True)
    username = StringField(max_length=80, required=True, unique=True)
    email = StringField(max_length=120, required=True, unique=True)
    full_name = StringField(max_length=120)  # Celebrity's display name
    password_hash = StringField(max_length=200, required=True)
    is_admin = BooleanField(default=False)  # Admin flag
    is_celebrity = BooleanField(default=True)  # Celebrity/user flag
    created_at = DateTimeField(default=datetime.utcnow)

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

      




