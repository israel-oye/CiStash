import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from oauthlib.oauth2 import WebApplicationClient

from extensions import (NotFound, current_user, db, login_required, login_user,
                        logout_user)
from models.moderator import Moderator

from ..utils.form import RegisterForm
from ..utils.mail import send_email
from ..utils.token import confirm_token, generate_token


auth_bp = Blueprint("auth_bp", __name__, template_folder="templates/auth", static_folder="static")

load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider():
    try:
        r = requests.get(GOOGLE_DISCOVERY_URL)
    except requests.exceptions.RequestException as e:
        print(e)
        abort(500)
    else:
        return r.json()

def send_verification_link(user: Moderator):
    token = generate_token(user.email)
    confirm_url = url_for("auth_bp.confirm_email", token=token, _external=True)
    mail_html = render_template("auth/confirm_mail.html", confirm_url=confirm_url, username=user.username)
    subject = "StashIT | Please confirm your mail"

    send_email(mail_recipient=user.email, mail_subject=subject, template=mail_html)

google_provider_cfg = get_google_provider()

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("resource_bp.upload"))

    register_form = RegisterForm(request.form)

    if request.method == "POST" and register_form.validate_on_submit():
        uname = register_form.username.data
        mail = register_form.email.data
        pwd = register_form.password.data

        mod = Moderator(username=uname, email=mail, password=pwd)
        db.session.add(mod)
        db.session.commit()

        send_verification_link(user=mod)

        login_user(mod)
        db.session.add(mod)
        db.session.commit()

        flash("Please confirm your mail before proceeding.", "info")
        return redirect(url_for("auth_bp.inactive"))

    return render_template("auth/register.html", form=register_form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("resource_bp.upload"))

    if request.method == "POST":
        current_app.logger.debug(request.form.to_dict())
        current_app.logger.debug(request.get_data(parse_form_data=True))

        input_email = request.form.get("email")
        input_pwd = request.form.get("password")

        try:
            user = Moderator.query.filter_by(email=input_email).first_or_404()
        except NotFound as e:
            error = "Incorrect email/password combination"
            return render_template("auth/login.html", error=error)
        else:
            if user.password_is_correct(password_candidate=input_pwd):
                login_user(user=user)
                flash(f"Login success. Welcome {current_user.username}!", "success")
                return redirect(url_for("resource_bp.upload"))
            else:
                error = "Incorrect password/email combination"
                return render_template("auth/login.html", error=error)
    return render_template("auth/login.html")


@auth_bp.route("/confirm/<token>")
@login_required
def confirm_email(token):
    if current_user.is_verified:
        flash("Account already confirmed.", "info")
        return redirect(url_for('resource_bp.upload'))
    to_be_verified_email = confirm_token(token)
    moderator = Moderator.query.filter_by(email=current_user.email).first()
    if moderator is not None and moderator.email == to_be_verified_email:
        moderator.is_verified = True
        moderator.confirmed_on = datetime.now()

        db.session.add(moderator)
        db.session.commit()
        flash("Your email has been confirmed. Thanks!", "success")
        return redirect(url_for('resource_bp.upload'))
    else:
        flash("The confirmation link is invalid or has expired.", "danger")
        return redirect(url_for("auth_bp.resend_confirmation"))


@auth_bp.route("/inactive")
@login_required
def inactive():
    if current_user.is_verified:
        return redirect(url_for('resource_bp.upload'))
    send_verification_link(user=current_user)
    return render_template("auth/inactive.html")


@auth_bp.route("/resend")
@login_required
def resend_confirmation():
    if current_user.is_verified:
        flash("Your account has already been verified.", "info")
        return redirect(url_for('resource_bp.upload'))
    send_verification_link(user=current_user)
    flash("A new confirmation link has been sent to your email.", "success")
    return redirect(url_for('auth_bp.inactive'))


@auth_bp.route("/google/login", methods=["POST"])
def oauth_login():
    global google_provider_cfg
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        uri=authorization_endpoint,
        redirect_uri=request.base_url+"/callback",
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)


@auth_bp.route("/google/login/callback")
def oauth_login_callback():
    code = request.args.get("code")

    global google_provider_cfg
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_url=token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        url=token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )

    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]

    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(
        url=uri,
        headers=headers,
        data=body
    )
    user_info = userinfo_response.json()
    if user_info.get("email_verified"):
        unique_id = user_info['sub']
        user_mail = user_info['email']
        user_name = user_info['given_name']
    else:
        flash("Email not verified. Please try again...", "danger")
        return redirect(url_for("auth_bp.register"))

    user = Moderator.query.filter_by(email=user_mail).first()
    if user is None:
        new_user = Moderator(username=user_name, email=user_mail, password=unique_id)
        db.session.add(new_user)
        db.session.commit()
        login_user(user=new_user)
        flash(f"{current_user.username}, you're now a contributor!", "success")
    else:
        login_user(user=user)
        flash(f"Login success. Welcome, {current_user.username}!", "success")
    return redirect(url_for("resource_bp.upload"))


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out", 'success')
    return redirect(url_for("auth_bp.login"))

