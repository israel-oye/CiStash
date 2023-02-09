from flask import Blueprint, flash, render_template, redirect, url_for, request
from extensions import login_manager, current_user, login_user, db, ValidationError
from models.admin import Moderator
from .form import RegisterForm
from passlib.hash import sha256_crypt

auth_bp = Blueprint("auth_bp", __name__, template_folder="src/templates", static_folder="static")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home_bp.index"))
    
    if request.method == "POST":
        input_email = request.form.get("email")
        input_pwd = request.form.get("password")
        
        try:
            user = Moderator.query.get_or_404(email=input_email)
        except:
            error = "Incorrect email/password combination"
            return render_template("login.html", error=error)
        else:
            if user.password_is_correct(sha256_crypt.encrypt(input_pwd)):
                flash("Login successful!", "success")
                login_user(user=user)
                return redirect(url_for("auth_bp.upload"))
            else:
                error = "Incorrect password/email combination"
                return render_template("login.html", error=error)
                

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home_bp.index"))

    register_form = RegisterForm(request.form)

    if request.method == "POST" and register_form.validate_on_submit():
        uname = register_form.username.data
        mail = register_form.email.data
        pwd = sha256_crypt.encrypt(str(register_form.password.data))

        mod = Moderator(username=uname, email=mail, password=pwd)
        db.session.add(mod)
        db.session.commit()
        login_user(mod)
        flash("Successfully registered.", "success")
        return redirect(url_for("home_bp.index"))


    return render_template("register.html", form=register_form)