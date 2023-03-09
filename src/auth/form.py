from extensions import FlaskForm, StringField, PasswordField, EmailField, SelectField, InputRequired, ValidationError
from wtforms import validators
from models.admin import Moderator
from models.course import Course
from models.level import LevelEnum

class RegisterForm(FlaskForm):
    username = StringField("Username", [validators.Length(3, 25, "Username must be at least %(min)d long!")], render_kw={"autofocus": True, "class": "form-control", "placeholder": "Username"})
    email = EmailField("Email", [InputRequired("Please enter an email!")], render_kw={"class": "form-control", "placeholder": "Email"})
    password = PasswordField("Password", [InputRequired(), validators.EqualTo("confirm", message="Passwords do not match!")], render_kw={"class": "form-control", "placeholder": "Password"})
    confirm = PasswordField("Confirm Password", render_kw={"class": "form-control", "placeholder": "Confirm password"})

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
                        [validators.Length(7, 7, "Please enter a valid course code."),  ],
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
        if selected_level.data not in [l.value for l in LevelEnum]:
            raise ValidationError("Please select a valid level.")
    
    def validate_course_code(self, course_code_field):
        if Course.query.filter_by(course_code=course_code_field.data).first():
            raise ValidationError(f"Oops, {course_code_field.data} has been registered.")
        
    def validate_course_title(self, course_title_field):
        if Course.query.filter_by(course_title=course_title_field.data).first():
            raise ValidationError(f"It seems like this course has been registered, please check carefully and try again.")
    