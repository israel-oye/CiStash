from datetime import datetime

from extensions import ModelView, db


class TimestampMixin:
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    modified = db.Column(db.DateTime, onupdate=datetime.utcnow)


class Document(db.Model, TimestampMixin):
    __tablename__ = "document"

    id_ = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True)
    filename = db.Column(db.String(255))
    file_size = db.Column(db.String(10))
    download_link = db.Column(db.Text)

    course_id = db.Column(db.Integer, db.ForeignKey("course.id_"))
    course = db.relationship("Course", back_populates="course_docs")

    uploader_id = db.Column(db.Integer, db.ForeignKey("moderator.id_"))
    uploader = db.relationship("Moderator", back_populates="uploads")

    def __repr__(self) -> str:
        return f"<Document: {self.filename}>"


class DocumentView(ModelView):
    can_create = False
    can_edit = True
    can_delete = True
    edit_modal = True
    form_widget_args = {
        'created': {
                'readonly': True,
                'disabled': True
        },
        'download_link': {
                'readonly': True
        },
        'modified': {
                'readonly': True,
                'disabled': True
        },
        'uploader': {
                'readonly': True,
        },
        'uuid': {
                'disabled': True
        },
    }