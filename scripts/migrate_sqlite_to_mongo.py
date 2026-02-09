"""Migration script: copy data from local SQLite (legacy_models) into MongoDB documents.

NOTICE: Make sure you have set your MONGO_URI environment variable pointing to MongoDB Atlas,
and your local data.db SQLite file exists with data.

Usage:
  python scripts/migrate_sqlite_to_mongo.py

This script will:
1. Read from SQLite (data.db) via SQLAlchemy legacy models
2. Write to MongoDB (MONGO_URI) via MongoEngine models
3. Preserve user passwords and all data
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=" * 70)
print("MongoDB Migration Script - SQLite to MongoDB Atlas")
print("=" * 70)
print()

# Check if MONGO_URI is set - try from environment first, then from instance/.env
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    # Try loading directly from the file
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', '.env'))
    print(f"Looking for MONGO_URI in: {env_path}")
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Debug: print all lines that mention MONGO
            for line in content.split('\n'):
                if 'MONGO' in line:
                    print(f"  Found line with MONGO: {line[:80]}")
            
            # Now extract MONGO_URI properly
            for line in content.split('\n'):
                stripped = line.strip()
                if stripped.startswith('MONGO_URI='):
                    mongo_uri = stripped.split('=', 1)[1].strip()
                    if mongo_uri.startswith('"') and mongo_uri.endswith('"'):
                        mongo_uri = mongo_uri[1:-1]
                    print(f"✓ Found MONGO_URI in file")
                    break
    except FileNotFoundError:
        print(f"  File not found: {env_path}")
    except Exception as e:
        print(f"  Warning: Could not read file: {e}")

if not mongo_uri:
    print("❌ ERROR: MONGO_URI environment variable is not set!")
    print("Please set MONGO_URI in instance/.env")
    sys.exit(1)

print(f"✓ Using MONGO_URI: {mongo_uri[:60]}...")
print()

from app import create_app
from urllib.parse import quote_plus
import re
import mongoengine as me

def encode_mongo_uri(mongo_uri):
    """Encode MongoDB URI credentials according to RFC 3986"""
    if not mongo_uri:
        return mongo_uri
    
    match = re.match(r'(mongodb\+srv://|mongodb://)([^:]+):([^@]+)@(.+)', mongo_uri)
    
    if match:
        protocol = match.group(1)
        username = match.group(2)
        password = match.group(3)
        rest = match.group(4)
        
        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password)
        
        encoded_uri = f"{protocol}{encoded_username}:{encoded_password}@{rest}"
        return encoded_uri
    
    return mongo_uri

# Encode the URI to handle special characters
encoded_mongo_uri = mongo_uri  # Use as-is since it's already encoded in the .env file

# Set the MONGO_URI in environment so create_app() will use it
os.environ['MONGO_URI'] = mongo_uri

app = create_app()

# Explicitly reconnect to MongoDB with the URI to ensure connection
try:
    me.disconnect('default')  # Disconnect from any previous connection
    me.connect(host=encoded_mongo_uri)
    print("✓ Connected to MongoDB Atlas for migration")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    sys.exit(1)

print()

with app.app_context():
    # Import legacy SQLAlchemy models and MongoEngine models
    from app.legacy_models import LegacyCelebrity, LegacyUser, LegacyCelebritySubmission, LegacyOnboardingRegistration
    from app.models import Celebrity, User, CelebritySubmission, OnboardingRegistration
    from app import DB
    
    # Initialize SQLAlchemy if not already initialized
    if 'sqlalchemy' not in app.extensions:
        DB.init_app(app)

    print('Starting migration from SQLite to MongoDB...')
    print()

    # Migrate Celebrities
    celebs_migrated = 0
    for lc in LegacyCelebrity.query.all():
        if Celebrity.objects(slug=lc.slug).first():
            print(f"Skipping existing celebrity: {lc.slug}")
            continue
        c = Celebrity(
            id=lc.id,
            name=lc.name,
            slug=lc.slug,
            bio=lc.bio,
            category=lc.category,
            photo_filename=lc.photo_filename,
            youtube=lc.youtube,
            tiktok=lc.tiktok,
            spotify=lc.spotify,
            featured=lc.featured,
            created_at=lc.created_at,
        )
        c.save()
        celebs_migrated += 1
        print(f"✓ Migrated celebrity: {lc.name}")

    # Migrate Users (passwords preserved via password_hash)
    users_migrated = 0
    for lu in LegacyUser.query.all():
        if User.objects(username=lu.username).first():
            print(f"Skipping existing user: {lu.username}")
            continue
        u = User(id=lu.id, username=lu.username, password_hash=lu.password_hash)
        u.save()
        users_migrated += 1
        print(f"✓ Migrated user: {lu.username} (password hash preserved)")

    # Migrate Submissions
    subs_migrated = 0
    for ls in LegacyCelebritySubmission.query.all():
        if CelebritySubmission.objects(id=ls.id).first():
            print(f"Skipping existing submission: {ls.id}")
            continue
        s = CelebritySubmission(
            id=ls.id,
            name=ls.name,
            email=ls.email,
            phone=ls.phone,
            category=ls.category,
            bio=ls.bio,
            youtube=ls.youtube,
            tiktok=ls.tiktok,
            spotify=ls.spotify,
            photo_filename=ls.photo_filename,
            status=ls.status,
            created_at=ls.created_at,
        )
        s.save()
        subs_migrated += 1
        print(f"✓ Migrated submission: {ls.id}")

    # Migrate Onboarding registrations
    onb_migrated = 0
    for lr in LegacyOnboardingRegistration.query.all():
        if OnboardingRegistration.objects(id=lr.id).first():
            print(f"Skipping existing onboarding: {lr.id}")
            continue
        r = OnboardingRegistration(
            id=lr.id,
            name=lr.name,
            email=lr.email,
            phone=lr.phone,
            message=lr.message,
            status=lr.status,
            created_at=lr.created_at,
        )
        r.save()
        onb_migrated += 1
        print(f"✓ Migrated onboarding: {lr.id}")

    print()
    print("=" * 70)
    print(f"Migration Summary:")
    print(f"  Celebrities:  {celebs_migrated}")
    print(f"  Users:        {users_migrated} (passwords preserved via hash)")
    print(f"  Submissions:  {subs_migrated}")
    print(f"  Onboarding:   {onb_migrated}")
    print("=" * 70)
    print()
    print('Migration complete. Your data and passwords are now in MongoDB.')
    print()

