# from ..home import home_bp
from typing import SupportsInt
from flask import current_app, redirect, request, render_template, url_for, Blueprint
home_bp = Blueprint('home_bp', __name__, template_folder="templates", static_folder="static")


@home_bp.get("/")
def index():
    # current_app.logger.info(request.path.split('/'))
    lvls = [
        {'id': 1, 'name': 100},
        {'id': 2, 'name': 200},
        {'id': 3, 'name': 300},
        {'id': 4, 'name': 400}
    ]
    return render_template("index.html", levels=lvls)


# def get_segment(request): 
#     try:
#         segment = request.path.split('/')[-1]
#         if segment == '':
#             segment = 'index'
#         return segment    
#     except:
#         return None