from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin.s3 import S3FileAdmin
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user, login_fresh
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, EmailField, SelectField, ValidationError
from wtforms.validators import InputRequired
from flask import current_app

metadata = MetaData(
    naming_convention={
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
    }
)

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
login_manager = LoginManager()
crsf = CSRFProtect()
admin = Admin(template_mode='bootstrap4')

login_manager.blueprint_login_views = {"moderator": "auth_bp.login"}
login_manager.login_message = "Unauthorized access!"
login_manager.login_message_category = "danger"
login_manager.needs_refresh_message = (u"Session timedout, please re-login")
login_manager.needs_refresh_message_category = "info"


from models.course import CourseView, Course
from models.doc import DocumentView, Document
from models.moderator import ModeratorView, Moderator

admin.add_view(ModeratorView(Moderator, db.session))
admin.add_view(CourseView(Course, db.session))
admin.add_view(DocumentView(Document, db.session))
