import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import mongoengine as me
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail, Message
from app.mpesa import mpesa_bp


from dotenv import load_dotenv

# Load environment variables from instance/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'instance', '.env'))

# Initialize extensions
DB = SQLAlchemy()
migrate = Migrate()
# MongoEngine will be used when MONGO_URI is provided
ME = None
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
    # If a MONGO_URI env var is present, connect MongoEngine and prefer MongoDB
    mongo_uri = os.getenv('MONGO_URI')
    if mongo_uri:
        # Use MongoEngine for production (Render)
        me.connect(host=mongo_uri)
    else:
        # Local development: Try to connect to local MongoDB, fall back to in-memory mock if unavailable
        try:
            me.connect('mongodb://localhost:27017/celebhub_local')
        except Exception as e:
            # If local MongoDB not available, use in-memory mock (mongoengine will work but won't persist)
            print(f"⚠️  Local MongoDB not available: {e}")
            print("📝 Using in-memory MongoEngine (data will not persist)")
            me.connect('mongoenginetest')
        
        # Also initialize SQLAlchemy as fallback
        DB.init_app(app)
        migrate.init_app(app, DB)

    global ME
    ME = me

    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Register Blueprints
    from .routes import main_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(mpesa_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Create database tables for local SQLite (as backup, if needed)
    if not mongo_uri:
        with app.app_context():
            DB.create_all()

    return app
