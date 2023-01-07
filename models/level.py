from extensions import db

class Level(db.Model):
    __tablename__ = "level"

    id_ = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(3), unique=True)
    # courses = db.relationship("course", back_populates="course_level")

    def __repr__(self) -> str:
        return f"<Level>: {self.name}"