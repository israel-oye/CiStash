from datetime import datetime

from flask import abort, flash, make_response, redirect, url_for
from passlib.hash import sha256_crypt

from extensions import AdminIndexView, ModelView, UserMixin, current_user, db


users_x_roles = db.Table(
    "users_roles",
    db.Column("user_id", db.ForeignKey("moderator.id_")),
    db.Column("role_id", db.ForeignKey("role.id_")),
    db.Column("assigned_at", db.DateTime, default=datetime.utcnow)
)


class Role(db.Model):

    id_ = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    users = db.relationship("Moderator", secondary="users_roles", back_populates="roles")

    def __init__(self, role_name: str, role_description: str):
        self.name = role_name
        self.description = role_description

    def __repr__(self):
        return f"<Role: {self.name}>"

    def __str__(self):
        return self.name


class Moderator(db.Model, UserMixin):
    """Uploader, i.e Moderator user model or an Admin."""

    id_ = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    email_verified = db.Column(db.Boolean(), nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime())

    uploads = db.relationship("Document", back_populates="uploader", lazy="select")
    roles = db.relationship("Role", secondary="users_roles", back_populates="users")
    courses_added = db.relationship("Course", back_populates="added_by")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = sha256_crypt.encrypt(password)
        self.email_verified = False

        default_role = Role.query.filter_by(name="regular").first()
        if default_role:
            self.roles.append(default_role)
        else:
            new_default_role = Role(role_name="regular", role_description="Can upload files, can add course details.")
            self.roles.append(new_default_role)

    def __repr__(self) -> str:
        return f"<Moderator: {self.email}>"

    @property
    def is_authenticated(self):
        return super().is_authenticated

    @property
    def is_active(self):
        return super().is_active

    @property
    def is_admin(self):
        admin_role = Role.query.filter_by(name="admin").first()
        return admin_role in self.roles

    @property
    def is_verified(self):
        return self.email_verified

    @is_verified.setter
    def is_verified(self, value: bool):
        self.email_verified = bool(value)

    def get_id(self):
        return self.id_

    def password_is_correct(self, password_candidate: str):
        return sha256_crypt.verify(password_candidate, self.password)


#Flask-Admin Views

class ModeratorView(ModelView):
    can_create = False
    can_edit = True
    can_delete = True
    column_display_pk = True
    edit_modal = True
    column_exclude_list = ['password']
    column_list = ('username', 'email', 'email_verified', 'roles', 'confirmed_on')
    form_columns = ['username', 'email', 'email_verified', 'roles']
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
            'readonly': True,
            'disabled': True
        },
    }


class RoleView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    create_modal = True
    edit_modal = True
    column_list = ('name', 'description', 'users')


class IndexView(AdminIndexView):

    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return super().is_accessible()
        abort(403)

    def inaccessible_callback(self, name, **kwargs):
        flash("Out of bounds!", "warning")
        return make_response(redirect(url_for("home_bp.index")), 403)
