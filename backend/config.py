import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "please-change-this-secret")
    JWT_ACCESS_TOKEN_EXPIRES = 86400
    PROPAGATE_EXCEPTIONS = True


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'app.db'}"
    )
