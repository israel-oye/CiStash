from extensions import ModelView, db


class Course(db.Model):
    __tablename__ = "course"
    query: db.Query

    id_ = db.Column(db.Integer, primary_key=True)
    course_title = db.Column(db.String(60), unique=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_docs = db.relationship("Document", back_populates="course", lazy="dynamic")
    level_id = db.Column(db.Integer, db.ForeignKey("level.id_"))
    course_level = db.relationship("Level", back_populates="courses")

    def __repr__(self) -> str:
        return f"<Course: {self.course_code}>"


class CourseView(ModelView):
    can_create = False
    can_edit = True
    can_delete = True
    create_modal = True
    edit_modal = True