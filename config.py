import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    PERMANENT_SESSION_LIFETIME = timedelta(days=1, hours=6)
    SECURITY_PASSWORD_SALT = os.urandom(16)

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
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///../test.db"
    WTF_CSRF_ENABLED = False


class TestingConfig(Config):
    TESTING = True
    EXPLAIN_TEMPLATE_LOADING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///../test.db"
    SQLALCHEMY_ECHO = True
    WTF_CSRF_ENABLED = False

