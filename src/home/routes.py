from typing import SupportsInt
from flask import current_app, flash, redirect, request, render_template, url_for, Blueprint
from models.level import Level

home_bp = Blueprint('home_bp', __name__, template_folder="src/templates", static_folder="src/static")


@home_bp.app_errorhandler(404)
def page_not_found(error):
    msg = "404 Error: Page Not Found. It looks like you're lost, but don't worry. Try using the search bar or returning to the homepage to find what you're looking for."
    return render_template("errors/404.html", msg=msg), 404

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