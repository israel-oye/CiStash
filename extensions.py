from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, EmailField, ValidationError
from wtforms.validators import InputRequired

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
crsf = CSRFProtect()


login_manager.blueprint_login_views = {"auth_bp": "login"}
login_manager.login_message = "Unauthorized access!"
login_manager.login_message_category = "danger"
login_manager.needs_refresh_message = (u"Session timedout, please re-login")
login_manager.needs_refresh_message_category = "info"
