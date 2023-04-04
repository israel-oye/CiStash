from extensions import db
import enum

class LevelEnum(enum.Enum):
    ONE = "100"
    TWO = "200"
    THREE = "300"
    FOUR = "400"

class Level(db.Model):
    __tablename__ = "level"

    id_ = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(LevelEnum), nullable=False, unique=True)
    courses = db.relationship("Course", back_populates="course_level")

    def __repr__(self) -> str:
        return f"<Level: {self.name.value}>"