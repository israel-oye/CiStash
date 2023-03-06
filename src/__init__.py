import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate, crsf, login_manager
from models.admin import Moderator

from .home import home_bp
from .auth import auth_bp
from config import DevelopmentConfig

load_dotenv()

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)

crsf.init_app(app)
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Moderator.query.get(int(user_id))

app.register_blueprint(home_bp, url_prefix="/home")
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    app.run()