from config import Config
from flasgger import Swagger
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.swagger import SWAGGER_CONFIG, SWAGGER_TEMPLATE

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    from app.routes.location_routes import location_bp
    from app.routes.analysis_routes import analysis_bp

    app.register_blueprint(location_bp)
    app.register_blueprint(analysis_bp)

    @app.get("/health")
    def health():
        """Service health check.
        ---
        tags:
          - Health
        responses:
          200:
            description: Service is up
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: UP
        """
        return {"status": "UP"}, 200

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database tables created.")

    return app
