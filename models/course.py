from extensions import db

class Course(db.Model):
    __tablename__ = "course"

    id_ = db.Column(db.Integer, primary_key=True)
    course_title = db.Column(db.String(60))
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    # course_docs = db.relationship("document", back_populates="course")
    # course_level = db.relationship("level", back_populates="courses")

    def __repr__(self) -> str:
        return f"<Course>: {self.course_code}" 
