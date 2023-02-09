from extensions import FlaskForm, StringField, PasswordField, EmailField, InputRequired, ValidationError
from wtforms import validators
from models.admin import Moderator

class RegisterForm(FlaskForm):
    username = StringField("Username", [validators.Length(3, 25, "Username must be at least %(min)d long!")], render_kw={"autofocus": True, "class": "form-control", "placeholder": "Username"})
    email = EmailField("Email", [InputRequired("Please enter an email!")], render_kw={"class": "form-control", "placeholder": "Email"})
    password = PasswordField("Password", [InputRequired(), validators.EqualTo("confirm", message="Passwords do not match!")], render_kw={"class": "form-control", "placeholder": "Password"})
    confirm = PasswordField("Confirm Password", render_kw={"class": "form-control", "placeholder": "Confirm password"})

    def validate_email(self, email):
        if Moderator.query.filter_by(email=email.data).first():
            raise ValidationError("Account exists for this email address!")
    
    def validate_username(self, username):
        if Moderator.query.filter_by(username=username.data).first():
            raise ValidationError("Username is not available!")