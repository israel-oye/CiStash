from tempfile import NamedTemporaryFile

from flask import (Blueprint, abort, current_app, jsonify, render_template,
                   send_file)
from urllib3.exceptions import ReadTimeoutError

from models.course import Course
from models.doc import Document

from ..auth.routes import bucket

resource_bp = Blueprint("resource_bp", __name__, template_folder="src/templates", static_folder="src/static")


@resource_bp.get("/course/<int:course_id>")
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    course_docs = course.course_docs.all()
    is_empty = False if bool(len(course_docs)) else True

    context = {
        "course": course,
        "course_docs": course_docs,
        "is_empty": is_empty
    }

    return render_template("course_page.html", **context)


@resource_bp.get("/document/<file_uuid>/download")
def download_document(file_uuid):
    doc = Document.query.filter_by(uuid=file_uuid).first()
    if not doc:
        return jsonify({"message": "The requested resource does not exist!"}), 400

    try:
        downloaded_file = bucket.download_file_by_id(file_id=doc.uuid)
    except ReadTimeoutError as e:
        current_app.logger.exception(e)
        return jsonify({"message": "An error occured while downloading...Please, try again."}), 500

    with NamedTemporaryFile(delete=False) as temp_file:
        downloaded_file.save(temp_file.file)
        temp_file.seek(0)

        resp = send_file(
            path_or_file=temp_file.name,
            as_attachment=True,
            download_name=doc.filename
        )
    return resp, 200

