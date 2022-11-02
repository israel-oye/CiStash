# from ..home import home_bp
from flask import current_app, redirect, request, render_template, url_for, Blueprint
home_bp = Blueprint('home_bp', __name__, template_folder="templates", static_folder="static")

@home_bp.get("/")
def index():
    # current_app.logger.info(request.path.split('/'))
    
    return render_template("index.html")


# def get_segment(request): 
#     try:
#         segment = request.path.split('/')[-1]
#         if segment == '':
#             segment = 'index'
#         return segment    
#     except:
#         return None