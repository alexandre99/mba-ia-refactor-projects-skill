from dataclasses import dataclass
import os
import secrets


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    secret_key: str
    debug: bool
    host: str
    port: int
    database_path: str
    environment: str
    admin_token: str
    seed_admin_password: str

    @classmethod
    def from_env(cls):
        return cls(
            secret_key=os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32),
            debug=_as_bool(os.environ.get("FLASK_DEBUG"), default=False),
            host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")),
            database_path=os.environ.get("DATABASE_PATH", "loja.db"),
            environment=os.environ.get("APP_ENV", "producao"),
            admin_token=os.environ.get("ADMIN_TOKEN", ""),
            seed_admin_password=os.environ.get("SEED_ADMIN_PASSWORD") or secrets.token_urlsafe(24),
        )
