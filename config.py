import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv(override=True)

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", default=os.urandom(32))
    PERMANENT_SESSION_LIFETIME = timedelta(days=2, hours=12)
    SECURITY_PASSWORD_SALT = os.urandom(32)

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True

    FLASK_ADMIN_SWATCH = 'Solar'

    MAIL_DEFAULT_SENDER="noreply@flask.com"
    MAIL_SERVER="smtp.googlemail.com"
    MAIL_PORT=465
    MAIL_USE_TLS=False
    MAIL_USE_SSL=True
    MAIL_DEBUG=False
    MAIL_USERNAME=os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")


class ProductionConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///../test.db"
    WTF_CSRF_ENABLED = False


class TestingConfig(Config):
    TESTING = True
    EXPLAIN_TEMPLATE_LOADING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///../test.db"
    SQLALCHEMY_ECHO = False
    WTF_CSRF_ENABLED = False


class LifeWireConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL_PROD_TEST")
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    WTF_CSRF_ENABLED = False

