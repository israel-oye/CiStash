from datetime import datetime

from extensions import ModelView, db


class Course(db.Model):
    __tablename__ = "course"

    id_ = db.Column(db.Integer, primary_key=True)
    course_title = db.Column(db.String(60), unique=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    added_on = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    course_docs = db.relationship("Document", back_populates="course", lazy="dynamic")

    level_id = db.Column(db.Integer, db.ForeignKey("level.id_"))
    course_level = db.relationship("Level", back_populates="courses")

    contributor_id = db.Column(db.Integer, db.ForeignKey("moderator.id_"))
    added_by = db.relationship("Moderator", back_populates="courses_added")

    def __repr__(self) -> str:
        return f"<Course: {self.course_code}>"

    @property
    def has_documents(self):
        return bool(self.course_docs.first())


class CourseView(ModelView):
    column_list = ('course_level', 'course_code', 'course_title', 'added_by', 'added_on')

    can_create = False
    can_edit = True
    can_delete = True
    create_modal = True
    edit_modal = True