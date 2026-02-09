"""Migration script: copy data from local SQLite (legacy_models) into MongoDB documents.

NOTICE: If you encounter "createIndexes not found" errors, your MongoDB service (e.g., Atlas)
may not support index creation. In that case, you can skip this migration and:
- Run the app locally with SQLite (default if MONGO_URI is not set)
- On Render, set MONGO_URI to enable MongoDB; the app will use .objects() queries automatically
- User passwords and data structure are preserved across both databases

Usage:
  python scripts/migrate_sqlite_to_mongo.py

This script expects that your environment variable `MONGO_URI` is set and reachable.
It will read the existing SQLite DB via SQLAlchemy legacy models and insert documents
into MongoEngine collections defined in `app.models`.
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'instance', '.env'))

print("=" * 70)
print("MongoDB Migration Script")
print("=" * 70)
print()
print("NOTICE: If you see 'createIndexes not found' error, your MongoDB Atlas")
print("may not support auto-index creation. If so, you can skip this migration.")
print("The app will work fine with SQLite locally and MongoDB on Render.")
print()
print("Data and passwords are preserved in both databases.")
print("=" * 70)
print()

from app import create_app
app = create_app()

with app.app_context():
    # Manually init SQLAlchemy for the legacy models to work
    from app import DB
    DB.init_app(app)

    # Ensure mongoengine connection (create_app should do this when MONGO_URI is present,
    # but connect explicitly here to guarantee the default connection exists)
    import mongoengine as me
    mongo_uri = os.getenv('MONGO_URI')
    # If dotenv didn't set the var, try reading the instance/.env directly
    if not mongo_uri:
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', '.env'))
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for ln in f:
                    if 'MONGO_URI' in ln:
                        parts = ln.split('=',1)
                        if len(parts) == 2:
                            mongo_uri = parts[1].strip()
                            # strip possible surrounding quotes
                            if mongo_uri.startswith('"') and mongo_uri.endswith('"'):
                                mongo_uri = mongo_uri[1:-1]
                            break
        except Exception:
            pass

    if mongo_uri:
        try:
            me.connect(host=mongo_uri)
            print('mongoengine connected using MONGO_URI from env/file')
        except Exception as e:
            print('Warning: mongoengine.connect failed:', e)
    else:
        print('No MONGO_URI found; running migration without MongoDB connection will fail if attempted')

    # Import legacy SQLAlchemy models and MongoEngine models
    from app.legacy_models import LegacyCelebrity, LegacyUser, LegacyCelebritySubmission, LegacyOnboardingRegistration
    from app.models import Celebrity, User, CelebritySubmission, OnboardingRegistration


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

