import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail, Message

from dotenv import load_dotenv

# Load environment variables from instance/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'instance', '.env'))

# Initialize extensions
DB = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'admin.login'
csrf = CSRFProtect()
mail = Mail()  # new

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # --- Core Configurations ---
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-this')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), '..', 'data.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB

    # --- Flask-Mail Configuration ---
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == "True"
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    

    # Initialize extensions
    DB.init_app(app)
    migrate.init_app(app, DB)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Register Blueprints
    from .routes import main_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Create database tables
    with app.app_context():
        DB.create_all()

    return app
