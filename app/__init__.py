from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Remover trailing slash
    app.url_map.strict_slashes = False

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Middleware CORS
    from app.middleware import setup_cors_middleware

    setup_cors_middleware(app)

    # Registrar blueprints
    from app.routes import register_blueprints

    register_blueprints(app)

    return app
