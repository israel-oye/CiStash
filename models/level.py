import enum

from extensions import db, ModelView


class LevelEnum(enum.Enum):
    ONE = "100"
    TWO = "200"
    THREE = "300"
    FOUR = "400"
    FIVE = "500"

class Level(db.Model):
    __tablename__ = "level"

    id_ = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(LevelEnum), nullable=False, unique=True)
    courses = db.relationship("Course", back_populates="course_level", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Level: {self.name.value}>"


class LevelView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
