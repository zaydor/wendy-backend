from datetime import datetime
from flask import Blueprint, session, redirect

from helpers import (
    login_required,
    validate_form,
    LoginForm,
    RegistrationForm,
    FirebaseHelper,
)


class AuthRoutes:
    def __init__(self):
        self.auth_bp = Blueprint("auth", __name__)
        self.firebase_helper = FirebaseHelper.get_instance()
        self.auth = self.firebase_helper.auth
        self.db = self.firebase_helper.db
        self.register_routes()

    def register_routes(self):
        bp = self.auth_bp
        auth = self.auth
        db = self.db

        @bp.route("/")
        def home():
            import socket

            return f"Hello World! {socket.gethostname()}"

        @bp.route("/login", methods=["GET"])
        def login():
            return """
            <h1>Login</h1>
            <form method="post" action="http://localhost/result">
              Email: <input name="email"><br>
              Password: <input name="password" type="password"><br>
              <button type="submit">Log In</button>
            </form>
            <a href="http://localhost/register">Create an account</a>
            """

        @bp.route("/register", methods=["GET"])
        def register_get():
            return """
            <h1>Register</h1>
            <form method="post" action="http://localhost/register">
              Email: <input name="email"><br>
              Password: <input name="password" type="password"><br>
              Confirm Password: <input name="confirm" type="password"><br>
              Name: <input name="name"><br>
              <button type="submit">Register</button>
            </form>
            <a href="http://localhost/login">Already a user?</a>
            """

        @bp.route("/register", methods=["POST"])
        @validate_form(RegistrationForm)
        def register_post(form):
            email = form.email.data
            password = form.password.data
            name = form.name.data
            try:
                auth.create_user_with_email_and_password(email, password)
                user = auth.sign_in_with_email_and_password(email, password)
                session["is_logged_in"] = True
                session["email"] = email
                session["uid"] = user["localId"]
                session["name"] = name
                data = {
                    "name": name,
                    "email": email,
                    "last_logged_in": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                }
                db.child("users").child(session["uid"]).set(data)
                return redirect("/authorize")
            except Exception as e:
                bp.logger.error(f"Error: {e}")
                bp.logger.error("Registration failed. Please try again.")
                return redirect("/register")

        @bp.route("/result", methods=["GET"])
        @login_required
        def result_get():
            return redirect("/profile")

        @bp.route("/result", methods=["POST"])
        @validate_form(LoginForm)
        def result_post(form):
            email = form.email.data
            password = form.password.data
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                session["is_logged_in"] = True
                session["email"] = email
                session["uid"] = user["localId"]

                data = db.child("users").get().val()

                if data and session["uid"] in data:
                    session["name"] = data[session["uid"]].get("name", "User")
                    session["refresh_token"] = data[session["uid"]].get("refresh_token")
                    db.child("users").child(session["uid"]).update(
                        {
                            "last_logged_in": datetime.now().strftime(
                                "%m/%d/%Y, %H:%M:%S"
                            )
                        }
                    )
                else:
                    session["name"] = "User"

                return redirect("/profile")
            except Exception as e:
                bp.logger.error(f"Error: {e}")
                return redirect("/login")

        @bp.route("/profile")
        @login_required
        def profile():
            return f"""
            <h1>Hello, {session.get("name")}</h1>
            <br>
            <a href='/logout'>Logout</a>
            <br>
            <a href='/authorize'>Authorize Spotify</a>
            <br>
            <a href='/spotifytoken'>Get Spotify Token</a>
            <br>
            <a href='/playlists'>Get Playlists</a>
            <br>
            <a href='/playlists/tracks'>Get Playlist Tracks</a>
            """

        @bp.route("/logout")
        @login_required
        def logout():
            db.child("users").child(session["uid"]).update(
                {"last_logged_out": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
            )
            session["is_logged_in"] = False
            return redirect("/login")
