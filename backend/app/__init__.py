import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_object='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_object)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    CORS(app, resources={r'/api/*': {'origins': ['http://localhost:5173', 'http://127.0.0.1:5173']}}, supports_credentials=True)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.claims import claims_bp
    from app.routes.intelligence import intelligence_bp
    from app.routes.admin import admin_bp
    from app.routes.analytics import analytics_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(claims_bp, url_prefix='/api')
    app.register_blueprint(intelligence_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    @app.get('/api/health')
    def health():
        return {'status': 'ok', 'database': 'PostgreSQL'}
    return app
