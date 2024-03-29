from flask import Blueprint, abort, redirect, render_template

from extensions import CSRFError
from models.course import Course
from models.level import Level, LevelEnum

from ..utils.form import CourseForm


home_bp = Blueprint(
    "home_bp", __name__, template_folder="templates/home", static_folder="src/static"
)


@home_bp.app_errorhandler(403)
def page_not_found(error):
    return render_template("errors/403.html"), 403


@home_bp.app_errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


# For production only
@home_bp.app_errorhandler(500)
def internal_server_error(error):
    return render_template("errors/500.html"), 500


@home_bp.app_errorhandler(CSRFError)
def csrf_error(error):
    return render_template("errors/csrf-error.html"), 400


@home_bp.get("/")
def index():
    return render_template("home/index.html")


@home_bp.get("/terms-of-privacy")
def privacy_page():
    return render_template("home/privacy.html")


@home_bp.get("/credits")
def credits_page():
    return render_template("home/acknowledgements.html")


@home_bp.get("/level/<int:level_id>")
def level_page(level_id):
    level = Level.query.get(level_id)

    if not level:
        abort(404)
    form = CourseForm(levels=level.name.name)   #level.name is an Enum obj
    level_courses = level.courses.order_by(Course.course_code).all()
    return render_template(
        "home/level_page.html", form=form, level=level, level_courses=level_courses
    )
