from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)

from models.level import Level, LevelEnum

home_bp = Blueprint('home_bp', __name__, template_folder="src/templates", static_folder="src/static")


@home_bp.app_errorhandler(404)
def page_not_found(error):
    msg = "404 Error: Page Not Found. It looks like you're lost, but don't worry. Try using the search bar or returning to the homepage to find what you're looking for."
    return render_template("errors/404.html", msg=msg), 404


@home_bp.get("/")
def index():
    return render_template("index.html")


@home_bp.get("/level/<int:level_id>")
def level_page(level_id):
    level = Level.query.get(level_id)

    if not level:
        abort(404)
    return render_template("level_page.html", level=level)