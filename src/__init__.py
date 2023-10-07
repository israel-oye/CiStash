from flask import Flask, session

from config import DevelopmentConfig, ProductionConfig, TestingConfig
from extensions import admin, crsf, db, login_manager, mail, migrate, IntegrityError
from models.level import Level, LevelEnum
from models.moderator import IndexView, Moderator

from .auth import auth_bp
from .home import home_bp
from .resource import resource_bp


def initialize_extensions(app: Flask):
    crsf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    admin.init_app(app, index_view=IndexView(name='Admin', url="/auth/admin"))
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Moderator.query.get(int(user_id))

def register_blueprints(app: Flask):
    app.register_blueprint(home_bp, url_prefix="/home")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(resource_bp, url_prefix="/resource")

def create_app(config_filename=None):
    app = Flask(__name__)

    app.config.from_object(TestingConfig)

    initialize_extensions(app)
    register_blueprints(app)

    with app.app_context():
        db.create_all()

        levels = []
        for l in LevelEnum:
            new_level = Level(name=l.name)
            levels.append(new_level)

        try:
            db.session.add_all(levels)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    @app.context_processor
    def utility_processor():
        def get_file_format(file_name: str):
            return file_name.split('.')[-1]

        lvls = {level.name: level.value for level in LevelEnum}
        return dict(get_file_format=get_file_format, lvl_mapping=lvls)


    return app
