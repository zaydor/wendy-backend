from datetime import datetime
from functools import wraps

from flask import redirect, request, session
from models import ErrorResponse


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("is_logged_in", False):
            return f(*args, **kwargs)
        return ErrorResponse(status=403, error="User not logged in").build()

    return decorated_function


def active_spotify_session_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        expires_in = session.get("expires_in", None)
        if expires_in is None:
            return redirect("/spotifytoken")
        if datetime.now().timestamp() >= expires_in:
            return redirect("/spotifytoken")
        return f(*args, **kwargs)

    return decorated_function


def validate_form(form_class):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Handle both JSON and form data
            if request.is_json:
                # Convert JSON to form-compatible data
                json_data = request.get_json()
                from werkzeug.datastructures import MultiDict
                form_data = MultiDict(json_data)
            else:
                form_data = request.form
            
            form = form_class(form_data)
            if not form.validate():
                return ErrorResponse(
                    message="Form validation failed", error=form.errors, status=402
                ).build()
            return f(*args, form=form, **kwargs)

        return decorated_function

    return decorator
