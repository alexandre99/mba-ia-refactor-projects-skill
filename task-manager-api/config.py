import os
import secrets


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_config():
    environment = os.getenv("APP_ENV", "development").strip().lower()
    secret_key = os.getenv("SECRET_KEY")
    if environment in {"production", "prod"} and not secret_key:
        raise RuntimeError("SECRET_KEY must be configured in production")

    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    debug = _as_bool(os.getenv("FLASK_DEBUG"), default=False)
    if environment in {"production", "prod"}:
        debug = False

    return {
        "APP_ENV": environment,
        "SECRET_KEY": secret_key or secrets.token_urlsafe(32),
        "SQLALCHEMY_DATABASE_URI": os.getenv("DATABASE_URL", "sqlite:///tasks.db"),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "DEBUG": debug,
        "HOST": os.getenv("HOST", "127.0.0.1"),
        "PORT": int(os.getenv("PORT", "5000")),
        "CORS_ORIGINS": [origin.strip() for origin in origins.split(",") if origin.strip()],
        "TOKEN_MAX_AGE": int(os.getenv("TOKEN_MAX_AGE", "86400")),
        "SMTP_HOST": os.getenv("SMTP_HOST"),
        "SMTP_PORT": int(os.getenv("SMTP_PORT", "587")),
        "SMTP_USER": os.getenv("SMTP_USER"),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
    }
