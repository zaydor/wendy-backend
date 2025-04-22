from flask import Flask, jsonify, request, session
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

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


@app.route("/")
def home():
    return "Hello World!"


@app.route("/login")
def login():
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
