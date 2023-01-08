from flask import Blueprint, flash, render_template, redirect, url_for
from extensions import login_manager
from models.admin import Admin

auth_bp = Blueprint("auth_bp", __name__, template_folder="templates", static_folder="static")

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(user_id)

@auth_bp.route("/")
def login():
    return render_template()