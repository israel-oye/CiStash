from ..models import db

class Document(db.Model):
    __tablename__ = "document"

    document_id = db.Column(db.Integer, primary_key=True)
    document_file = db.Column(db.LargeBinary)
    # course_id = db.Column(db.Integer, db.ForeignKey("course.course_id"))
    # course = db.relationship("course", back_populates="course_docs")