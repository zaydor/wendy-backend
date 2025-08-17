from datetime import datetime

from flask import Blueprint, session, request
from helpers import (
    FirebaseHelper,
    LoginForm,
    RegistrationForm,
    login_required,
    validate_form,
)
from models import DataResponse, ErrorResponse, StandardResponse


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
                # Create user with Admin SDK
                user_record = auth.create_user(
                    email=email,
                    password=password,
                    display_name=name
                )
                
                session["is_logged_in"] = True
                session["email"] = email
                session["uid"] = user_record.uid
                session["name"] = name
                
                data = {
                    "name": name,
                    "email": email,
                    "last_logged_in": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                }
                db.child("users").child(session["uid"]).set(data)

                user_data = {
                    "name": session["name"],
                    "email": session["email"],
                    "uid": session["uid"],
                }
                return DataResponse(message="Registration successful", data=user_data).build()
            except Exception as e:
                return ErrorResponse(
                    message="Registration failed", status=401, error=str(e)
                ).build()

        @bp.route("/login", methods=["POST"])
        @validate_form(LoginForm)
        def login(form):
            email = form.email.data
            password = form.password.data
            try:                
                # Get user details with Admin SDK
                user_record = auth.get_user_by_email(email)
                
                session["is_logged_in"] = True
                session["email"] = email
                session["uid"] = user_record.uid

                data = db.child("users").get()

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
                    session["name"] = user_record.display_name or "User"
                
                user_data = {
                    "name": session["name"],
                    "email": session["email"],
                    "uid": session["uid"],
                }

                return DataResponse(message="Login successful", data=user_data).build()
            except Exception as e:
                return ErrorResponse(
                    message="Login failed", status=401, error=str(e)
                ).build()

        @bp.route("/logout")
        def logout():
            # Only update database if user was actually logged in
            if session.get("is_logged_in") and session.get("uid"):
                db.child("users").child(session["uid"]).update(
                    {"last_logged_out": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
                )
            
            # Clear the session completely
            session.clear()
            return StandardResponse(message="Logout successful").build()

        @bp.route("/me")
        @login_required
        def me():
            user_data = {
                "name": session["name"],
                "email": session["email"],
                "uid": session["uid"],
            }
            return DataResponse(data=user_data).build()
