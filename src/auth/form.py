from extensions import FlaskForm, StringField, PasswordField, InputRequired

class LoginForm(FlaskForm):
    username = StringField("username", InputRequired("Please enter a username"))
    password = PasswordField("password", InputRequired())