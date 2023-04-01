from extensions import db, ModelView

class Document(db.Model):
    __tablename__ = "document"

    id_ = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True)
    filename = db.Column(db.String(255))
    download_link = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id_"))
    course = db.relationship("Course", back_populates="course_docs")
    uploader_id = db.Column(db.Integer, db.ForeignKey("moderator.id_"))
    uploader = db.relationship("Moderator", back_populates="uploads")

    def __repr__(self) -> str:
        return f"<Document: {self.uuid}>"
    
    
class DocumentView(ModelView):
    can_create = False
    can_edit = False
    can_delete = True
    