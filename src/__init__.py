import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate

from .home import home_bp
from config import DevelopmentConfig

load_dotenv()

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)
app.config["EXPLAIN_TEMPLATE_LOADING"] = True

db.init_app(app)
migrate.init_app(app)

app.register_blueprint(home_bp)


if __name__ == "__main__":
    app.run()