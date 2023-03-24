from flask import Blueprint, current_app, flash, render_template, redirect, url_for, request, jsonify
from werkzeug.datastructures import ImmutableMultiDict
from extensions import login_manager, current_user, login_user, login_required, logout_user, db
from models.moderator import Moderator
from models.course import Course
from .form import RegisterForm, CourseForm
from passlib.hash import sha256_crypt

auth_bp = Blueprint("auth_bp", __name__, template_folder="src/templates", static_folder="static")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth_bp.upload"))

    register_form = RegisterForm(request.form)

    if request.method == "POST" and register_form.validate_on_submit():
        uname = register_form.username.data
        mail = register_form.email.data
        pwd = sha256_crypt.encrypt(str(register_form.password.data))

        mod = Moderator(username=uname, email=mail, password=pwd)
        db.session.add(mod)
        db.session.commit()
        
        flash("Successfully registered. Please log in.", "success")
        return redirect(url_for("auth_bp.login"))

    return render_template("register.html", form=register_form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth_bp.upload"))
    
    if request.method == "POST":
        
        input_email = request.form.get("email")
        input_pwd = request.form.get("password")
        
        try:
            user = Moderator.query.filter_by(email=input_email).first_or_404()
        except Exception as e:
            error = "User not found"
            return render_template("login.html", error=error)
        else:
            if user.password_is_correct(password_candidate=input_pwd):
                flash("Login successful!", "success")
                login_user(user=user)
                return redirect(url_for("auth_bp.upload"))
            else:
                error = "Incorrect password/email combination"
                return render_template("login.html", error=error)
                

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out", 'success')
    return redirect(url_for("auth_bp.login"))

@auth_bp.route("/upload", methods=['GET'])
@login_required
def get_upload_page():
    form = CourseForm()
    form.dyna_course_code.choices = [(course.id_, course.course_code) for course in Course.query.order_by("course_code")]

    return render_template("upload.html", form=form)

@auth_bp.route("/upload", methods=["POST"])
@login_required
def upload():

    form = CourseForm(data=request.get_json())
    
    if form.validate_on_submit():
        new_course = Course(
            course_title=str(form.course_title.data).title(),
            course_code=form.course_code.data
            )
        try:
            db.session.add(new_course)
            db.session.commit()
        except Exception as e:
            return jsonify({"message": "An error occurred while saving, please try again."}), 500
        return jsonify({"message": "Course added successfully", "redirect_url": "/pass"}), 200 #TODO probably add redirect link. 
                                                                                               #"redirect_url": url_for(home.index)
    else:
        errors = form.errors
        return jsonify({"errors": errors}), 400

@auth_bp.route("/file_upload", methods=["POST"])
@login_required
def file_upload():
    ...