from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)

from models.course import Course
from models.level import Level, LevelEnum

home_bp = Blueprint('home_bp', __name__, template_folder="src/templates", static_folder="src/static")


@home_bp.app_errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@home_bp.get("/")
def index():
    return render_template("index.html")


@home_bp.get("/level/<int:level_id>")
def level_page(level_id):
    level = Level.query.get(level_id)

    if not level:
        abort(404)

    level_courses = level.courses.order_by(Course.course_code).all()
    return render_template("level_page.html", level=level, level_courses=level_courses)