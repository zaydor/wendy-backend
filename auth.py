from functools import wraps
from flask import session, redirect


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("is_logged_in", False):
            return f(*args, **kwargs)
        return redirect("/login")

    return decorated_function
