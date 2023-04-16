from flask import flash, make_response, redirect, url_for
from passlib.hash import sha256_crypt

from extensions import AdminIndexView, ModelView, UserMixin, current_user, db


class Moderator(db.Model, UserMixin):
    """Uploader, i.e Moderator user model or an Admin."""
    query: db.Query

    id_ = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    uploads = db.relationship("Document", back_populates="uploader", lazy="select")

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
    can_create = False
    can_edit = False
    can_delete = False


class IndexView(AdminIndexView):

    def is_accessible(self):
        if current_user.is_authenticated and current_user.id_ == 1:
            return super().is_accessible()
        return False

    def inaccessible_callback(self, name, **kwargs):
        flash("Out of bounds!", "warning")
        return make_response(redirect(url_for("home_bp.index")), 403)
