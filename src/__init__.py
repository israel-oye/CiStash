import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate

from .home import home_bp
from .auth import auth_bp
from config import DevelopmentConfig

load_dotenv()

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)

db.init_app(app)
migrate.init_app(app)

app.register_blueprint(home_bp, url_prefix="/home")
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    app.run()