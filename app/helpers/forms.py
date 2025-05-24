from wtforms import Form, PasswordField, StringField, validators


class RegistrationForm(Form):
    name = StringField("name", [validators.Length(min=1, max=50)])
    email = StringField("email", [validators.Length(min=6, max=50), validators.Email()])
    password = PasswordField(
        "password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Confirm Password")


class LoginForm(Form):
    email = StringField("email", [validators.Length(min=6, max=50), validators.Email()])
    password = PasswordField(
        "password",
        [
            validators.DataRequired(),
        ],
    )
