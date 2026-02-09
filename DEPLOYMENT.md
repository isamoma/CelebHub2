# MongoDB + Render Deployment Guide

## Overview
This app now supports **dual database modes**:
- **Local development**: SQLite (default, no setup needed)
- **Production (Render)**: MongoDB (when `MONGO_URI` environment variable is set)

**Your passwords are preserved in both modes** via Flask-WTF's `generate_password_hash()`.

---

## Local Development (SQLite)

No special setup needed. The app uses local SQLite by default:

```bash
pip install -r requirements.txt
python manage.py
```

The app will:
- Use `data.db` (SQLite)
- Not require MongoDB connection
- Work exactly as before

---

## Deploying to Render with MongoDB

### Step 1: Prepare MongoDB

Use **MongoDB Atlas** (free tier available):
1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Create a database access user with a strong password
4. Copy the connection string (replace `<password>` and `<database_name>`)
5. Connection format:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
   ```

### Step 2: Set Environment Variables on Render

In your Render service settings, add:

```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database_name?retryWrites=true&w=majority
SECRET_KEY=<your-secret-key>
MPESA_CONSUMER_KEY=<your-key>
MPESA_CONSUMER_SECRET=<your-secret>
MAIL_SERVER=<your-mail-server>
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=<your-email>
MAIL_PASSWORD=<your-password>
MAIL_DEFAULT_SENDER=<your-sender>
```

### Step 3: Deploy

Push your code to GitHub. Render will:
1. Install dependencies from `requirements.txt`
2. Detect `manage.py` as the entry point
3. Read `MONGO_URI` from environment variables
4. The app will automatically use MongoDB when `MONGO_URI` is set

---

## Understanding the Database Switch

### How it works:

**In `app/__init__.py`:**
```python
mongo_uri = os.getenv('MONGO_URI')
if mongo_uri:
    # Use MongoDB via MongoEngine
    me.connect(host=mongo_uri)
else:
    # Use SQLite via Flask-SQLAlchemy
    DB.init_app(app)
    DB.create_all()
```

### Data Structure:

**MongoEngine models** (`app/models.py`):
- `Celebrity` → collection `celebrities`
- `User` → collection `users` (passwords preserved as `password_hash`)
- `CelebritySubmission` → collection `celebrity_submissions`
- `OnboardingRegistration` → collection `onboarding_registrations`

All password hashes are portable between SQLite and MongoDB.

---

## Migrating Data from Local SQLite to MongoDB (Optional)

If you want to migrate existing local data:

```bash
# Ensure MONGO_URI is set in instance/.env
python scripts/migrate_sqlite_to_mongo.py
```

This script:
1. Reads all records from local `data.db` (SQLite)
2. Writes them to MongoDB
3. **Preserves all password hashes**
4. Skips duplicates

**Note**: If you see `createIndexes not found` error, your MongoDB may not support auto-indexing. In that case, the app will still work fine without migration—just set `MONGO_URI` on Render and start fresh with MongoDB.

---

## Admin User

**Local (SQLite):**
```bash
python create_admin.py
# Enter username and password
```

**On Render (MongoDB):**
Same command works. The password will be stored in MongoDB with the same hash.

---

## Testing

**Local CSRF tests:**
```bash
python -u scripts/test_csrf.py
```

**Live Render test:**
- Visit your Render app URL
- Log in with admin credentials (same password from local)
- Create/edit/delete celebrities
- All data saves to MongoDB

---

## Troubleshooting

### "ModuleNotFoundError: mongoengine"
- Run: `pip install mongoengine pymongo`

### "MONGO_URI not found"
- Ensure `instance/.env` has a `MONGO_URI=...` line, OR
- Set `MONGO_URI` directly in Render environment variables

### "Connection refused" to MongoDB
- Check MongoDB Atlas firewall rules allow your Render IP
- Test connection string in MongoDB Atlas "Test Connection"

### Data not appearing on Render
- Check that your `MONGO_URI` is set in Render environment (not local `instance/.env`)
- Render loads env vars from dashboard/settings, not from pushed files

---

## Summary

✅ Your app now supports both SQLite (local) and MongoDB (Render)
✅ Passwords are preserved and portable
✅ No database migrations required (but optional)
✅ Same codebase for local and production
✅ Admin users work identically in both modes
