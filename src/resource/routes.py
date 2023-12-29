import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import b2sdk.v2 as b2
from b2sdk.v2.exception import B2Error
from dotenv import load_dotenv
from flask import (Blueprint, abort, current_app, jsonify, render_template, request,
                   send_file)
from urllib3.exceptions import ReadTimeoutError
from werkzeug.utils import secure_filename

from extensions import (NotFound, SQLAlchemyError, current_user, db,
                        login_required)
from models.course import Course
from models.doc import Document
from models.level import Level, LevelEnum

from ..utils.form import CourseForm, UpdateCourseForm
from ..utils.decorators import verification_required

load_dotenv()

resource_bp = Blueprint("resource_bp", __name__, template_folder="templates/resource", static_folder="src/static")

temp_dir = Path(__file__).resolve().parent.parent / "static" / "temp"
if not temp_dir.exists():
    temp_dir.mkdir()


def init_backblaze():
    try:
        b2_info = b2.InMemoryAccountInfo()
        b2_encryption_setting = b2.EncryptionSetting(mode=b2.EncryptionMode.SSE_B2, algorithm=b2.EncryptionAlgorithm.AES256)
        b2_api = b2.B2Api(b2_info)
        b2_api.authorize_account(
            "production",
            application_key_id=os.getenv("B2_KEY_ID"),
            application_key=os.getenv("B2_APPLICATION_KEY")
        )
        bucket: b2.bucket.Bucket = b2_api.get_bucket_by_name(os.getenv("B2_UPLOAD_BUCKET_NAME"))
    except B2Error as e:
        current_app.logger.error(e, exc_info=True)
        abort(500)
    except Exception as e:
        current_app.logger.error(e, exc_info=True)
        abort(500)
    else:
        return bucket, b2_api, b2_encryption_setting


@resource_bp.get("/course/<courseID:identifier>")
def get_course(identifier):
    if identifier.isdigit():
        course = Course.query.get_or_404(int(identifier))
    else:
        course = Course.query.filter_by(course_code=identifier).first_or_404()
    course_docs = course.course_docs.all()
    is_empty = False if bool(len(course_docs)) else True

    form = UpdateCourseForm(obj=course)
    form.set_model_instance(course)

    context = {
        "course": course,
        "course_docs": course_docs,
        "is_empty": is_empty,
        "form": form
    }

    return render_template("resource/course_page.html", **context)


@resource_bp.get("/document/<file_uuid>/download")
def download_document(file_uuid):
    b2_objects = init_backblaze()
    bucket = b2_objects[0]

    doc = Document.query.filter_by(uuid=file_uuid).first()
    if not doc:
        return jsonify({"message": "The requested resource does not exist!"}), 400

    try:
        downloaded_file = bucket.download_file_by_id(file_id=doc.uuid)
    except ReadTimeoutError as e:
        current_app.logger.exception(e)
        return jsonify({"message": "An error occured while downloading...Please, try again."}), 500
    except B2Error as e:
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
    user_query = request.form.get("searched").strip()

    course_query = Course.query \
    .filter(
        Course.course_code.ilike(f"%{user_query}%")
        | Course.course_title.ilike(f"%{user_query}%")
          ) \
    .order_by(Course.course_code) \
    .distinct()

    document_query = Document.query \
                    .filter(Document.filename.ilike('%'+user_query+'%')) \
                    .order_by(Document.filename) \
                    .distinct()

    is_empty = None
    if (course_query.count() or document_query.count()) and user_query != '':
        is_empty = False
    else:
        is_empty = True

    context = {
        "search_query": user_query,
        "is_empty": is_empty,
        "no_courses_match": False if course_query.count() else True,
        "no_docs_match": False if document_query.count() else True,
        "course_hits": course_query.count(),
        "document_hits": document_query.count(),
        "hits": course_query.count() + document_query.count(),
        "courses": course_query.all(),
        "documents": document_query.all()
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
    form.course_code_dropdown.choices = []
    return render_template("resource/upload.html", form=form)


@resource_bp.post("/add-course")
def upload_course():
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
            current_app.logger.exception(e)
            return jsonify({"message": "An error occurred while saving, please try again."}), 500
        else:
            return jsonify({"message": "Course added successfully", "redirect_url": "/pass"}), 200 #TODO probably add redirect link.
                                                                                               #"redirect_url": url_for(home.index)
    else:
        errors = form.errors
        return jsonify({"errors": errors}), 400


@resource_bp.post("/edit-course/<course_id>")
def edit_course(course_id):
    if not current_user.is_authenticated:
        return jsonify({'message': 'An error occured, please re-login to complete action'}), 401
    try:
        course = Course.query.get_or_404(course_id)
    except NotFound:
        return jsonify({"message": "The course you are trying to edit does not exist"}), 404

    form = UpdateCourseForm(data=request.get_json())
    form.set_model_instance(course)
    if form.validate_on_submit():
        course_level = Level.query.filter_by(name=LevelEnum[str(form.levels.data)].name).first()
        course.level_id = course_level.id_
        course.course_code = form.course_code.data
        course.course_title = form.course_title.data

        db.session.commit()
        return jsonify({"message": "Course updated successfully", "redirect_url": "/pass"}), 200
    else:
        errors = form.errors
        return jsonify({"errors": errors}), 400


@resource_bp.post("/file-upload")
@login_required
@verification_required
def file_upload():
    b2_objects = init_backblaze()
    bucket = b2_objects[0]
    b2_api = b2_objects[1]
    b2_encryption_setting = b2_objects[2]

    upload_status = request.headers.get('X-File-Status')
    file = request.files.get("file", None)

    if upload_status == 'canceled':
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)

            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        return jsonify({"message": "Upload canceled!", "code": 200}), 200

    if file:
        uploaded_file = file
        uploaded_file_uid = request.form['dzuuid']  #TODO Handle no JS fallback upload on Server-Side
        unique_filename = f"{uploaded_file_uid[:8]}_{secure_filename(uploaded_file.filename)}"

        current_chunk = int(request.form["dzchunkindex"])

        temp_file = Path(temp_dir / unique_filename)
        if current_chunk == 0:
            temp_file.touch()

        if upload_status == 'uploading':
            with open(temp_file, "ab") as f:
                f.seek(int(request.form["dzchunkbyteoffset"]))
                f.write(uploaded_file.stream.read())

            total_file_size = int(request.form.get("dztotalfilesize", "N/A"))
            total_chunks = int(request.form.get("dztotalchunkcount"))
            if current_chunk + 1 == total_chunks:
                if os.path.getsize(temp_file) != int(request.form["dztotalfilesize"]):
                    return jsonify({"message": "Size mismatch", "status": 400}), 400

                course_id = int(request.form["course_id"])
                document_course = Course.query.get(course_id)
                if not document_course:
                    return jsonify({"message": "Related course not found, please select a valid course from option above", "code": 400}), 400
                metadata = {
                    "filename": unique_filename[9:],
                    "unique_filename": unique_filename,
                    "document_course": document_course.course_code,
                    "document_size": format(total_file_size * (10**-6), ".2f")
                }

                try:
                    uploaded_bucket_file = bucket.upload_local_file(
                        local_file=temp_file,
                        file_name=metadata["unique_filename"],
                        file_infos=metadata,
                        encryption=b2_encryption_setting
                    )
                    download_url = b2_api.get_download_url_for_fileid(uploaded_bucket_file.id_)
                except Exception as e:
                    current_app.logger.error(e, exc_info=True)
                    return jsonify({"message": "An error occured while uploading, please try again...", "code": 500}), 500
                else:
                    new_document = Document(
                        uuid=uploaded_bucket_file.id_,
                        filename=metadata["filename"],
                        file_size=metadata["document_size"],
                        download_link=download_url,
                        course_id=document_course.id_,
                        uploader_id=current_user.id_
                    )
                    db.session.add(new_document)
                    db.session.commit()
                finally:
                    os.remove(temp_file)
            else:
                current_app.logger.debug(f"Chunk {current_chunk + 1} of {total_chunks} for file {secure_filename(uploaded_file.filename)} complete")

            return jsonify({"message": "Upload success!", "code": 200}), 200
        else:
            return jsonify({"message": "Upload canceled!", "code": 204}), 204
    else:
        return jsonify({"message": "Invalid/No file part in request body", "code": 400}), 400
