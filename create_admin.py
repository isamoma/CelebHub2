from getpass import getpass
import os
from app import create_app, DB
from app.models import User, USE_MONGO

app = create_app()

def create_admin_interactive():
  username = input("Admin username: ").strip()
  email = input("Admin email (optional): ").strip() or None
  if USE_MONGO:
    existing = User.objects(username=username).first()
  else:
    existing = User.query.filter_by(username=username).first()

  if existing:
    print("The username already exists.")
    return

  pw = getpass("Password: ")
  pw2 = getpass("Confirm password: ")
  if pw != pw2:
    print("Passwords do not match.")
    return

  u = User(username=username, email=email, is_admin=True)
  u.set_password(pw)
  if USE_MONGO:
    u.save()
  else:
    DB.session.add(u)
    DB.session.commit()
  print(f"Admin user '{username}' created.")

def create_admin_from_env():
  # Supports creating multiple admin usernames separated by commas
  admin_env = os.getenv('ADMIN_USERNAMES')
  admin_pw = os.getenv('ADMIN_PASSWORD')
  if not admin_env or not admin_pw:
    return False

  created = []
  for username in [u.strip() for u in admin_env.split(',') if u.strip()]:
    # use a default email if none
    email = f"{username}@example.com"
    if USE_MONGO:
      exists = User.objects(username=username).first()
    else:
      exists = User.query.filter_by(username=username).first()

    if exists:
      print(f"Admin '{username}' already exists, skipping.")
      continue

    u = User(username=username, email=email, is_admin=True)
    u.set_password(admin_pw)
    if USE_MONGO:
      u.save()
    else:
      DB.session.add(u)
      DB.session.commit()
    created.append(username)
    print(f"Admin '{username}' created.")

  return bool(created)


if __name__ == '__main__':
  # Try environment-driven creation first (non-interactive)
  with app.app_context():
    auto = create_admin_from_env()
    if auto:
      print("Admin creation via environment completed.")
    else:
      print("No ADMIN_USERNAMES/ADMIN_PASSWORD env set — running interactive creation.")
      create_admin_interactive()