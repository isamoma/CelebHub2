from getpass import getpass
from app import create_app,DB
from app.models import User

app= create_app()
with app.app_context():
  username=input("Admin username").strip()
  if User.query.filter_by(username=username).first():
    print("The username already exists.")
  else:
    pw= getpass("Password:")
    pw2=getpass("confirm password:")
    if pw!=pw2:
      print("Passwords do not match.")
    else:
      u= User(username=username)
      u.set_password(pw)
      DB.session.add(u)
      DB.session.commit()
      print("Admin user created.")