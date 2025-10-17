import os
from flask import Flask,render_templates
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'instance', '.env'))

DB = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'admin.login'
csrf = CSRFProtect()
app = Flask(__name__, instance_relative_config=True)
def create_app():
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-this')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(
        os.path.join(os.path.dirname(__file__), '..', 'data.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB upload limit

    DB.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .routes import main_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.app_context():
        DB.create_all()

    return app
