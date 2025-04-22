from datetime import datetime
from auth import login_required
from flask import Flask, flash, jsonify, redirect, request, session
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import pyrebase

# load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure session
app.secret_key = os.getenv("SECRET_KEY")

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET = os.getenv("SPOTIFY_SECRET")
REDIRECT_URI = "http://localhost:5050/callback"

# Spotify API endpoints
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"


# Firebase configuration
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", None),
    "serviceAccount": os.getenv("FIREBASE_SERVICE_ACCOUNT", None),
}

firebase = pyrebase.initialize_app(firebase_config)

# Get reference to Firebase auth and database
auth = firebase.auth()
db = firebase.database()


@app.route("/")
def home():
    return "Hello World!"


@app.route("/login", methods=["GET"])
def login():
    return """
    <h1>Login</h1>
    <form method="post" action="http://localhost:5050/result">
      Email: <input name="email"><br>
      Password: <input name="password" type="password"><br>
      <button type="submit">Log In</button>
    </form>
    <a href="http://localhost:5050/register">Create an account</a>
    """


@app.route("/register", methods=["GET"])
def register_get():
    return """
    <h1>Register</h1>
    <form method="post" action="http://localhost:5050/register">
      Email: <input name="email"><br>
      Password: <input name="password" type="password"><br>
      Name: <input name="name"><br>
      <button type="submit">Register</button>
    </form>
    <a href="http://localhost:5050/login">Already a user?</a>
    """


@app.route("/register", methods=["POST"])
def register_post():
    result = request.form
    email = result["email"]
    password = result["password"]
    name = result["name"]
    try:
        # create user in Firebase
        auth.create_user_with_email_and_password(email, password)
        # authenticate user
        user = auth.sign_in_with_email_and_password(email, password)
        session["is_logged_in"] = True
        session["email"] = email
        session["uid"] = user["localId"]
        session["name"] = name
        # save user data in Firebase
        data = {
            "name": name,
            "email": email,
            "last_logged_in": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        }
        db.child("users").child(session["uid"]).set(data)
        return redirect("/profile")
    except Exception as e:
        app.logger.error(f"Error: {e}")
        flash("Registration failed. Please try again.")
        return redirect("/register")


@app.route("/result", methods=["GET"])
@login_required
def result_get():
    return redirect("/profile")


@app.route("/result", methods=["POST"])
def result_post():
    result = request.form
    email = result["email"]
    password = result["password"]
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        session["is_logged_in"] = True
        session["email"] = email
        session["uid"] = user["localId"]

        data = db.child("users").get().val()

        if data and session["uid"] in data:
            session["name"] = data[session["uid"]]["name"]
            db.child("users").child(session["uid"]).update(
                {"last_logged_in": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
            )
        else:
            session["name"] = "User"

        return redirect("/profile")
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return redirect("/login")


@app.route("/profile")
@login_required
def profile():
    return f"Hello, {session.get('email')}<br><a href='/logout'>Logout</a>"


@app.route("/logout")
@login_required
def logout():
    db.child("users").child(session["uid"]).update(
        {"last_logged_out": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
    )
    session["is_logged_in"] = False
    return redirect("/login")


@app.route("/authorize")
def authorize():
    scope = "user-read-private user-read-playback-state user-modify-playback-state playlist-read-private"
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": scope,
    }
    response = requests.get(AUTH_URL, params=params)
    auth_url = response.url

    return jsonify({"auth_url": auth_url})


@app.route("/callback")
def callback():
    code = request.args.get("code")
    auth_options = {
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(
        TOKEN_URL,
        data=auth_options,
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_SECRET),
    )

    if response.status_code == 200:
        token_info = response.json()
        session["access_token"] = token_info["access_token"]
        session["refresh_token"] = token_info["refresh_token"]
        session["expires_in"] = token_info["expires_in"]
        return jsonify({"message": "Login successful", "token_info": token_info})
    return jsonify({"error": "Failed to get access token"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
