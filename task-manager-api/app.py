from flask import Flask
from flask_cors import CORS

from config import load_config
from database import db
from routes.category_routes import category_bp
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from utils.time import utcnow


def create_app(config_overrides=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(load_config())
    if config_overrides:
        app.config.update(config_overrides)

    CORS(app, origins=app.config["CORS_ORIGINS"])
    db.init_app(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(category_bp)

    @app.route("/health")
    def health():
        return {"status": "ok", "timestamp": str(utcnow())}

    @app.route("/")
    def index():
        return {"message": "Task Manager API", "version": "1.0"}

    return app


app = create_app()


if __name__ == "__main__":
    if app.config["APP_ENV"] in {"production", "prod"}:
        raise RuntimeError("Use a WSGI server with wsgi:app in production")
    app.run(
        debug=app.config["DEBUG"],
        host=app.config["HOST"],
        port=app.config["PORT"],
        use_reloader=False,
    )
