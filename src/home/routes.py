from typing import SupportsInt
from flask import current_app, redirect, request, render_template, url_for, Blueprint
from models.level import Level

home_bp = Blueprint('home_bp', __name__, template_folder="src/templates", static_folder="static")


@home_bp.get("/")
def index():
    # current_app.logger.info(request.path.split('/'))
    lvls = [
        {'id': 1, 'name': 100},
        {'id': 2, 'name': 200},
        {'id': 3, 'name': 300},
        {'id': 4, 'name': 400}
    ]
    # levels = Level.query.all()
    return render_template("index.html", levels=lvls)

@home_bp.get("/100")
def linker():
    return "<h3>Wagwan</h3>"
# def get_segment(request): 
#     try:
#         segment = request.path.split('/')[-1]
#         if segment == '':
#             segment = 'index'
#         return segment    
#     except:
#         return None