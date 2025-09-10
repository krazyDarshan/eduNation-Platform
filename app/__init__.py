from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Please login to access this page.'
    
    # Register blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.courses import bp as courses_bp
    app.register_blueprint(courses_bp, url_prefix='/courses')
    
    from app.routes.gamification import bp as gamification_bp
    app.register_blueprint(gamification_bp, url_prefix='/gamification')
    
    from app.routes.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))
