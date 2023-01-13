from extensions import db, UserMixin

class Moderator(db.Model, UserMixin):
    """Uploader, i.e Moderator user model"""
    id_ = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)

    @property
    def is_authenticated(self):
        return super().is_authenticated

    @property
    def is_active(self):
        return super().is_active

    def get_id(self):
        return super().get_id()
