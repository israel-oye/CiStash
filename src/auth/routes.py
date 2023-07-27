from flask import Blueprint, flash, redirect, render_template, request, url_for
from passlib.hash import sha256_crypt

from extensions import (NotFound, current_user, db, login_required, login_user,
                        logout_user)
from models.moderator import Moderator

from ..form import RegisterForm

auth_bp = Blueprint("auth_bp", __name__, template_folder="src/templates", static_folder="static")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("resource_bp.upload"))

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
        return redirect(url_for("resource_bp.upload"))

    if request.method == "POST":
        input_email = request.form.get("email")
        input_pwd = request.form.get("password")

        try:
            user = Moderator.query.filter_by(email=input_email).first_or_404()
        except NotFound as e:
            error = "Incorrect email/password combination"
            return render_template("login.html", error=error)
        else:
            if user.password_is_correct(password_candidate=input_pwd):
                login_user(user=user)
                flash(f"Login success. Welcome {current_user.username}!", "success")
                return redirect(url_for("resource_bp.upload"))
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

