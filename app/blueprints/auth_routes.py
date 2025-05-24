from datetime import datetime

from flask import Blueprint, session
from helpers import (
    FirebaseHelper,
    LoginForm,
    RegistrationForm,
    login_required,
    validate_form,
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

        @bp.route("/register", methods=["POST"])
        @validate_form(RegistrationForm)
        def register(form):
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
                return (
                    {
                        "Access-Control-Allow-Credentials": "true",
                        "message": "Login successful",
                        "user": {
                            "name": session["name"],
                            "email": session["email"],
                            "uid": session["uid"],
                        },
                    },
                    200,
                )
            except Exception as e:
                return (
                    {
                        "Access-Control-Allow-Credentials": "true",
                        "message": "Register failed",
                        "error": str(e),
                    },
                    401,
                )

        @bp.route("/login", methods=["POST"])
        @validate_form(LoginForm)
        def login(form):
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

                return (
                    {
                        "Access-Control-Allow-Credentials": "true",
                        "message": "Login successful",
                        "user": {
                            "name": session["name"],
                            "email": session["email"],
                            "uid": session["uid"],
                        },
                    },
                    200,
                )
            except Exception as e:
                return (
                    {
                        "Access-Control-Allow-Credentials": "true",
                        "message": "Login failed",
                        "error": str(e),
                    },
                    401,
                )

        @bp.route("/logout")
        @login_required
        def logout():
            db.child("users").child(session["uid"]).update(
                {"last_logged_out": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
            )
            session["is_logged_in"] = False
            return (
                {
                    "Access-Control-Allow-Credentials": "true",
                    "message": "Logout successful",
                },
                200,
            )

        # @bp.route("/profile")
        # @login_required
        # def profile():
        #     return f"""
        #     <h1>Hello, {session.get("name")}</h1>
        #     <br>
        #     <a href='/logout'>Logout</a>
        #     <br>
        #     <a href='/authorize'>Authorize Spotify</a>
        #     <br>
        #     <a href='/spotifytoken'>Get Spotify Token</a>
        #     <br>
        #     <a href='/playlists'>Get Playlists</a>
        #     <br>
        #     <a href='/playlists/tracks'>Get Playlist Tracks</a>
        #     """
