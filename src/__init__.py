import os

from dotenv import load_dotenv
from flask import Flask, session

from config import DevelopmentConfig
from extensions import admin, crsf, db, login_manager, migrate, IntegrityError
from models.level import Level, LevelEnum
from models.moderator import IndexView, Moderator

from .auth import auth_bp
from .home import home_bp
from .resource import resource_bp

load_dotenv()

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)

crsf.init_app(app)
db.init_app(app)
migrate.init_app(app, db, render_as_batch=True)
login_manager.init_app(app)
admin.init_app(app, index_view=IndexView(name='Admin', url="/auth/admin"))


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
def inject_levels():
    lvls = {level.name: level.value for level in LevelEnum}
    return dict(lvl_mapping=lvls)

@login_manager.user_loader
def load_user(user_id):
    return Moderator.query.get(int(user_id))

app.register_blueprint(home_bp, url_prefix="/home")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(resource_bp, url_prefix="/resource")

if __name__ == "__main__":
    app.run()