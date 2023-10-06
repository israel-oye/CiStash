import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import b2sdk.v2 as b2
from dotenv import load_dotenv
from flask import (Blueprint, current_app, jsonify, render_template, request,
                   send_file)
from urllib3.exceptions import ReadTimeoutError
from werkzeug.utils import secure_filename

from extensions import (NotFound, SQLAlchemyError, current_user, db,
                        login_required)
from models.course import Course
from models.doc import Document
from models.level import Level, LevelEnum

from ..utils.form import CourseForm
from ..utils.decorators import verification_required

load_dotenv()

resource_bp = Blueprint("resource_bp", __name__, template_folder="templates/resource", static_folder="src/static")


b2_info = b2.InMemoryAccountInfo()
b2_encryption_setting = b2.EncryptionSetting(mode=b2.EncryptionMode.SSE_B2, algorithm=b2.EncryptionAlgorithm.AES256)
b2_api = b2.B2Api(b2_info)
b2_api.authorize_account(
    "production",
    application_key_id=os.getenv("B2_KEY_ID"),
    application_key=os.getenv("B2_APPLICATION_KEY")
)
bucket = b2_api.get_bucket_by_name(os.getenv("UPLOAD_BUCKET_NAME"))

temp_dir = Path(__file__).resolve().parent.parent / "static" / "temp"


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

    return render_template("resource/course_page.html", **context)


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


@resource_bp.post("/search")
def search():
    user_query = request.form.get("searched")
    search_hits = []

    courses_from_code = Course.query.filter(Course.course_code.like('%'+user_query+'%'))
    search_hits += [course for course in courses_from_code.order_by(Course.course_code).all()]

    courses_from_title = Course.query.filter(Course.course_title.like('%'+user_query+'%'))
    search_hits += [course for course in courses_from_title.order_by(Course.course_code).all()]

    docs_from_filename = Document.query.filter(Document.filename.like('%'+user_query+'%'))
    doc_hits = [document for document in docs_from_filename.order_by(Document.filename).distinct().all()]

    context = {
        "search_query": user_query,
        "is_empty": False if len(search_hits) else True,
        "no_docs_match": False if len(doc_hits) else True,
        "hits": search_hits,
        "doc_hits": doc_hits,
        "result_count": len(search_hits) + len(doc_hits)
    }

    return render_template("resource/search.html", **context)


@resource_bp.get("/fetch/<level_name>/courses")
def get_level_courses(level_name):
    selected_level = Level.query.filter_by(name=level_name).first_or_404()
    level_courses = selected_level.courses.order_by(Course.course_code).all()

    course_array = []
    for course_obj in level_courses:
        course_array.append(
            {
                "id": course_obj.id_,
                "course_code": course_obj.course_code
            }
        )
    return jsonify({"courses": course_array}), 200


@resource_bp.get("/upload")
@login_required
@verification_required
def get_upload_page():
    form = CourseForm()
    form.dyna_course_code.choices = []
    return render_template("resource/upload.html", form=form)


@resource_bp.post("/upload")
def upload():
    if not current_user.is_authenticated:
        return jsonify({'message': 'An error occured, please re-login to complete action'}), 401

    form = CourseForm(data=request.get_json())

    if form.validate_on_submit():
        course_level = Level.query.filter_by(name=LevelEnum[str(form.levels.data)].name).first()
        new_course = Course(
            course_title=str(form.course_title.data).title(),
            course_code=form.course_code.data,
            level_id = course_level.id_
            )
        try:
            db.session.add(new_course)
            db.session.commit()
        except SQLAlchemyError as e:
            return jsonify({"message": "An error occurred while saving, please try again."}), 500
        except Exception as e:
            current_app.log_exception(e)
        else:
            return jsonify({"message": "Course added successfully", "redirect_url": "/pass"}), 200 #TODO probably add redirect link.
                                                                                               #"redirect_url": url_for(home.index)
    else:
        errors = form.errors
        return jsonify({"errors": errors}), 400


@resource_bp.post("/file_upload")
@login_required
@verification_required
def file_upload():
    file = request.files.get("file", None)
    if file:
        uploaded_file = file
        uploaded_file_uid = request.form['dzuuid']  #TODO Handle no JS fallback upload on Server-Side
        unique_filename = f"{uploaded_file_uid[:8]}_{secure_filename(uploaded_file.filename)}"

        current_chunk = int(request.form["dzchunkindex"])

        temp_file = Path(temp_dir / unique_filename)
        with open(temp_file, "ab") as f:
            f.seek(int(request.form["dzchunkbyteoffset"]))
            f.write(uploaded_file.stream.read())

        total_file_size = int(request.form.get("dztotalfilesize", "N/A"))
        total_chunks = int(request.form.get("dztotalchunkcount"))
        if current_chunk + 1 == total_chunks:
            if os.path.getsize(temp_file) != int(request.form["dztotalfilesize"]):
                return jsonify({"message": "Size mismatch", "status": 400}), 400

            course_id = int(request.form["course_id"])
            try:
                doc_course = Course.query.get_or_404(course_id)
            except NotFound:
                return jsonify({"message": "Related course not found, please select a valid course from option above", "code": 400}), 400
            except Exception as e:
                current_app.log_exception(e)
                return jsonify({"message": "Internal server error...", "code": 500}), 500
            metadata = {
                "filename": unique_filename[9:],
                "unique_filename": unique_filename,
                "document_course": doc_course.course_code,
                "document_size": format(total_file_size * (10**-6), ".2f")
            }
            global bucket
            bucket.update(default_server_side_encryption=b2_encryption_setting)
            try:
                uploaded_bucket_file = bucket.upload_local_file(
                    local_file=temp_file,
                    file_name=metadata["unique_filename"],
                    file_infos=metadata,
                    encryption=b2_encryption_setting
                )
                download_url = b2_api.get_download_url_for_fileid(uploaded_bucket_file.id_)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify({"message": "An error occured while uploading, please try again...", "code": 500}), 500
            else:
                try:
                    new_document = Document(
                        uuid=uploaded_bucket_file.id_,
                        filename=metadata["filename"],
                        file_size=metadata["document_size"],
                        download_link=download_url,
                        course_id=doc_course.id_,
                        uploader_id=current_user.id_
                    )
                    db.session.add(new_document)
                    db.session.commit()
                except SQLAlchemyError:
                    jsonify({"message": "An error occured while saving, please try again...", "code": 500}), 500
                except Exception as e:
                    current_app.log_exception(e)
            finally:
                os.remove(temp_file)
        else:
            current_app.logger.debug(f"Chunk {current_chunk + 1} of {total_chunks} for file {secure_filename(uploaded_file.filename)} complete")

        return jsonify({"message": "Upload success!", "code": 200}), 200
    else:
        return jsonify({"message": "Invalid/No file part in request body", "code": 400}), 400
