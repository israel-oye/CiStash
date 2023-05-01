import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

import b2sdk.v2 as b2
from dotenv import load_dotenv
from flask import (Blueprint, current_app, flash, jsonify, redirect,
                   render_template, request, url_for, make_response)
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename

from extensions import (current_user, db, login_manager, login_required,
                        login_user, logout_user, NotFound, InternalServerError, SQLAlchemyError)
from models.course import Course
from models.doc import Document
from models.level import Level, LevelEnum
from models.moderator import Moderator

from .form import CourseForm, RegisterForm

load_dotenv()


auth_bp = Blueprint("auth_bp", __name__, template_folder="src/templates", static_folder="static")


b2_info = b2.InMemoryAccountInfo()
b2_encryption_setting = b2.EncryptionSetting(mode=b2.EncryptionMode.SSE_B2, algorithm=b2.EncryptionAlgorithm.AES256)
b2_api = b2.B2Api(b2_info)
b2_api.authorize_account(
    "production",
    application_key_id=os.getenv("B2_KEY_ID"),
    application_key=os.getenv("B2_APPLICATION_KEY")
)
bucket = b2_api.get_bucket_by_name(os.getenv("UPLOAD_BUCKET_NAME"))

temp_dir = temp_file = Path(__file__).resolve().parent.parent / "static" / "temp"

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth_bp.upload"))

    register_form = RegisterForm(request.form)

    if request.method == "POST" and register_form.validate_on_submit():
        uname = register_form.username.data
        mail = register_form.email.data
        pwd = sha256_crypt.encrypt(str(register_form.password.data))

        mod = Moderator(username=uname, email=mail, password=pwd)
        db.session.add(mod)
        db.session.commit()

        flash("Successfully registered. Please log in.", "success")
        return redirect(url_for("auth_bp.login"))

    return render_template("register.html", form=register_form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth_bp.upload"))

    if request.method == "POST":
        input_email = request.form.get("email")
        input_pwd = request.form.get("password")

        try:
            user = Moderator.query.filter_by(email=input_email).first_or_404()
        except NotFound as e:
            error = "User not found"
            return render_template("login.html", error=error)
        else:
            if user.password_is_correct(password_candidate=input_pwd):
                flash("Login successful!", "success")
                login_user(user=user)
                return redirect(url_for("auth_bp.upload"))
            else:
                error = "Incorrect password/email combination"
                return render_template("login.html", error=error)
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out", 'success')
    return redirect(url_for("auth_bp.login"))

@auth_bp.route("/upload/<level_name>/courses")
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


@auth_bp.route("/upload", methods=['GET'])
@login_required
def get_upload_page():
    form = CourseForm()
    form.dyna_course_code.choices = []
    return render_template("upload.html", form=form)


@auth_bp.route("/upload", methods=["POST"])
@login_required
def upload():
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


@auth_bp.route("/file_upload", methods=["POST"])
@login_required
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
                "document_course": doc_course.course_code
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
