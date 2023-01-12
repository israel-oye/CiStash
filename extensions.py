from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
crsf = CSRFProtect()