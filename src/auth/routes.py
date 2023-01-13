from flask import Blueprint, flash, render_template, redirect, url_for
from extensions import login_manager
from models.admin import Moderator

auth_bp = Blueprint("auth_bp", __name__, template_folder="src/templates", static_folder="static")


@auth_bp.route("/login")
def login():
    return render_template()

@auth_bp.route("/register")
def register():
    ...