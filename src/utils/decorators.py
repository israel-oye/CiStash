from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def verification_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_verified is False:
            flash("Please, confirm your email", "warning")
            return redirect(url_for('auth_bp.inactive'))
        return func(*args, **kwargs)

    return decorated_function