from flask import abort, flash, make_response, redirect, url_for
from passlib.hash import sha256_crypt

from extensions import AdminIndexView, ModelView, UserMixin, current_user, db

ROLES = {
    "guest": 0,
    "moderator": 1,
    "admin": 2
}

class Moderator(db.Model, UserMixin):
    """Uploader, i.e Moderator user model or an Admin."""
    query: db.Query

    id_ = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    uploads = db.relationship("Document", back_populates="uploader", lazy="select")
    is_admin = db.Column(db.Boolean, default=False)
    role_number = db.Column(db.Integer(), nullable=False, default=ROLES['moderator'])

    @property
    def is_authenticated(self):
        return super().is_authenticated

    @property
    def is_active(self):
        return super().is_active

    def __repr__(self) -> str:
        return f"<Moderator: {self.email}>"

    def get_id(self):
        return self.id_

    def password_is_correct(self, password_candidate: str):
        return sha256_crypt.verify(password_candidate, self.password)


class ModeratorView(ModelView):
    can_create = True
    can_edit = True
    can_delete = False
    column_exclude_list = ['password']
    form_edit_rules = ('is_admin', 'role_number')
    form_widget_args = {
        'username': {
            'readonly': True
        },
        'email': {
            'readonly': True
        },
        'password': {
            'readonly': True
        },
        'uploads': {
            'readonly': True
        },
    }


class IndexView(AdminIndexView):

    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return super().is_accessible()
        abort(404)

    def inaccessible_callback(self, name, **kwargs):
        flash("Out of bounds!", "warning")
        return make_response(redirect(url_for("home_bp.index")), 403)
