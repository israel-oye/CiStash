from flask import current_app
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.fileadmin.s3 import S3FileAdmin
from flask_admin.contrib.sqla import ModelView
from flask_login import (LoginManager, UserMixin, current_user, login_fresh,
                         login_required, login_user, logout_user)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import MetaData
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import InternalServerError, NotFound
from wtforms import (EmailField, PasswordField, SelectField, StringField,
                     ValidationError)
from wtforms.validators import InputRequired

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


login_manager.login_view = "auth_bp.login"
login_manager.login_message = "Please login before proceeding..."
login_manager.login_message_category = "info"
login_manager.needs_refresh_message = (u"Session timedout, please re-login")
login_manager.needs_refresh_message_category = "info"


from models.course import Course, CourseView
from models.doc import Document, DocumentView
from models.level import Level, LevelView
from models.moderator import Moderator, ModeratorView, Role, RoleView

admin.add_view(ModeratorView(Moderator, db.session))
admin.add_view(RoleView(Role, db.session))
admin.add_view(CourseView(Course, db.session))
admin.add_view(DocumentView(Document, db.session))
admin.add_view(LevelView(Level, db.session))
