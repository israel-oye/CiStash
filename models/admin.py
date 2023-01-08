from extensions import db, UserMixin

class Admin(db.Model, UserMixin):
    ...