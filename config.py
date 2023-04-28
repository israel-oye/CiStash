import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    FLASK_ADMIN_SWATCH = 'Solar'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1, hours=6)

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
    WTF_CSRF_ENABLED = False

