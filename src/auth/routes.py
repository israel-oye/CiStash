from flask import Blueprint, flash, render_template, redirect, url_for

auth_bp = Blueprint("auth_bp", __name__, template_folder="templates", static_folder="static")

@auth_bp.get("/")
def index():
    return render_template()