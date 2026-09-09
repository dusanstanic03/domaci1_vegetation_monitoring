from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes.location_routes import location_bp

    app.register_blueprint(location_bp)

    @app.get("/health")
    def health():
        return {"status": "UP"}, 200

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database tables created.")

    return app
