from flask import Flask
from config import Config
from extensions import db, jwt, cors

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    
    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.medications import medications_bp
    from routes.doctors import doctors_bp
    from routes.reminders import reminders_bp
    from routes.prescriptions import prescriptions_bp
    from routes.users import users_bp
    from routes.notifications import notifications_bp
    from routes.media import media_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(medications_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(prescriptions_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(media_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✓ Database tables created!")
    
    return app
