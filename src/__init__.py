import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate, crsf, login_manager, admin
from models.moderator import Moderator, IndexView, ModeratorView
from models.course import Course, CourseView
from models.doc import Document, DocumentView


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
admin.init_app(app, index_view=IndexView(name='Admin',url="/auth/admin") )

# admin.add_view(ModeratorView(Moderator, db.session))
# admin.add_view(CourseView(Course, db.session))
# admin.add_view(DocumentView(Document, db.session))

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Moderator.query.get(int(user_id))

app.register_blueprint(home_bp, url_prefix="/home")
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
    app.run()