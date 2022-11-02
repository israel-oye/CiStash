from ..models import db

class Course(db.Model):
    __tablename__ = "course"

    course_id = db.Column(db.Integer, primary_key=True)
    course_title = db.Column(db.String(60))
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    # course_docs = db.relationship("document", back_populates="course")

    def __repr__(self) -> str:
        return f"<Course>: {self.course_name}" 
