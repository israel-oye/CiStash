from extensions import db

class Document(db.Model):
    __tablename__ = "document"

    id_ = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), unique=True)
    filename = db.Column(db.String(255))
    download_link = db.Column(db.Text)
    # course_id = db.Column(db.Integer, db.ForeignKey("course.id_"))
    # course = db.relationship("course", back_populates="course_docs")

    def __repr__(self) -> str:
        return f"<Document: {self.uuid}>"