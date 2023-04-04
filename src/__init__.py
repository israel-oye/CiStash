import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate, crsf, login_manager, admin
from models.moderator import Moderator, IndexView
from models.level import Level, LevelEnum


from .home import home_bp
from .auth import auth_bp
from config import DevelopmentConfig

load_dotenv()

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)

crsf.init_app(app)
db.init_app(app)
migrate.init_app(app, db, render_as_batch=True)
login_manager.init_app(app)
admin.init_app(app, index_view=IndexView(name='Admin',url="/auth/admin"))


with app.app_context():
    db.create_all()

    levels = []
    for l in LevelEnum:
        new_level = Level(name=l.name)
        levels.append(new_level)

    try:
        db.session.add_all(levels)
        db.session.commit()
    except Exception as e:
        pass
    
@app.context_processor
def inject_levels():
    lvls = {level.name: level.value for level in LevelEnum}
    return dict(lvl_mapping=lvls)

@login_manager.user_loader
def load_user(user_id):
    return Moderator.query.get(int(user_id))

app.register_blueprint(home_bp, url_prefix="/home")
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    app.run()