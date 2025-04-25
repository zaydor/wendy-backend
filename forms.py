from wtforms import Form, StringField, PasswordField, validators


class RegistrationForm(Form):
    name = StringField("Name", [validators.Length(min=1, max=50)])
    email = StringField("Email", [validators.Length(min=6, max=50), validators.Email()])
    password = PasswordField(
        "Password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Confirm Password")


class LoginForm(Form):
    email = StringField("Email", [validators.Length(min=6, max=50), validators.Email()])
    password = PasswordField(
        "Password",
        [
            validators.DataRequired(),
        ],
    )
