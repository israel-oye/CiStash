import re

from wtforms import validators

from extensions import (EmailField, FlaskForm, InputRequired, PasswordField,
                        SelectField, StringField, ValidationError)
from models.course import Course
from models.level import LevelEnum
from models.moderator import Moderator


class RegisterForm(FlaskForm):
    username = StringField(
                            "Username",
                            [InputRequired("Please enter a username"), validators.Length(3, 25, "Username must be at least %(min)d long!")],
                            render_kw={"autofocus": True, "class": "form-control", "placeholder": "Username"}
                            )
    email = EmailField(
                        "Email",
                        [InputRequired("Please enter an email!")],
                        render_kw={"class": "form-control", "placeholder": "Email"}
                        )
    password = PasswordField(
                            "Password",
                            [InputRequired(),
                            validators.EqualTo("confirm", message="Passwords do not match!")],
                            render_kw={"class": "form-control", "placeholder": "Password"}
                            )
    confirm = PasswordField("Confirm Password",
                            [InputRequired()],
                            render_kw={"class": "form-control", "placeholder": "Confirm password"}
                            )

    def validate_email(self, email):
        if Moderator.query.filter_by(email=email.data).first():
            raise ValidationError("Account exists for this email address")

    def validate_username(self, username):
        if Moderator.query.filter_by(username=username.data).first():
            raise ValidationError("Username is not available")

class CourseForm(FlaskForm):
    levels = SelectField(
                        "Course Level",
                        validate_choice=True,
                        default="Course Level",
                        choices=[(level.name, level.value) for level in LevelEnum],
                        render_kw={"class": "form-select", "aria-label": "Select level"}
                        )
    course_code = StringField(
                        "Course Code",
                        [InputRequired(), validators.Length(7, 7, "Please enter a valid course code."),  ],
                        render_kw={"class": "form-control", "placeholder": "e.g CSC 199"}
                        )
    course_title = StringField(
                        "Course Title",
                        [InputRequired()],
                        render_kw={"class": "form-control", "placeholder": "e.g Introduction to Web Development", "aria-placeholder": "e.g Introduction to Web Development"}
                        )
    dyna_course_code = SelectField(
                        'Course Code',
                        validate_choice=False,
                        choices=[],
                        render_kw={"class": "form-select", "aria-label": "Select course code"}
                        )

    def validate_levels(self, selected_level):
        if selected_level.data not in [l.name for l in LevelEnum]:
            raise ValidationError("Please select a valid level.")

    def validate_course_code(self, course_code_field):
        pattern = r"\b[A-Z]{3} \b(1[0-9]{2}|[2-5][0-9]{2}|599)\b"
        selected_level = LevelEnum[self.levels.data].value
        course_code_num = course_code_field.data.split()[-1] if course_code_field.data else [""]

        if Course.query.filter_by(course_code=course_code_field.data).first():
            raise ValidationError(f"Oops, {course_code_field.data} has been registered.")
        elif re.match(pattern, str(course_code_field.data)) is None:
            raise ValidationError("Please enter the course code correctly. e.g ABC 415 (All caps with a space in-between.)")
        elif selected_level[0] != course_code_num[0]:
            raise ValidationError("Please enter a valid course code for the selected level.")

    def validate_course_title(self, course_title_field):
        field_data = str(course_title_field.data).title()

        if Course.query.filter_by(course_title=field_data).first():
            raise ValidationError(f"It seems like this course has been registered, please check carefully and try again.")
