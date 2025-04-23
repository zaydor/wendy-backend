from functools import wraps
from flask import session, redirect
from datetime import datetime


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("is_logged_in", False):
            return f(*args, **kwargs)
        return redirect("/login")

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
