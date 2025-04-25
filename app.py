from datetime import datetime
from wrappers import login_required, active_spotify_session_required, validate_form
from flask import Flask, flash, jsonify, redirect, request, session
from flask_cors import CORS
from forms import RegistrationForm, LoginForm
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
      Confirm Password: <input name="confirm" type="password"><br>
      Name: <input name="name"><br>
      <button type="submit">Register</button>
    </form>
    <a href="http://localhost:5050/login">Already a user?</a>
    """


@app.route("/register", methods=["POST"])
@validate_form(RegistrationForm)
def register_post(form):
    email = form.email.data
    password = form.password.data
    name = form.name.data
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
        return redirect("/authorize")
    except Exception as e:
        app.logger.error(f"Error: {e}")
        flash("Registration failed. Please try again.")
        return redirect("/register")


@app.route("/result", methods=["GET"])
@login_required
def result_get():
    return redirect("/profile")


@app.route("/result", methods=["POST"])
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
            session["name"] = data[session["uid"]]["name"]
            session["refresh_token"] = data[session["uid"]]["refresh_token"]
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


@app.route("/logout")
@login_required
def logout():
    db.child("users").child(session["uid"]).update(
        {"last_logged_out": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
    )
    session["is_logged_in"] = False
    return redirect("/login")


@app.route("/authorize")
@login_required
def authorize():
    scope = "user-read-private user-read-email user-read-playback-state user-modify-playback-state playlist-read-private user-read-recently-played user-read-currently-playing playlist-modify-public playlist-modify-private"
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": scope,
    }
    response = requests.get(AUTH_URL, params=params)
    auth_url = response.url

    return redirect(auth_url)


@app.route("/callback")
@login_required
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
        db.child("users").child(session["uid"]).update(
            {"refresh_token": token_info["refresh_token"]}
        )
        session["access_token"] = token_info["access_token"]
        session["refresh_token"] = token_info["refresh_token"]
        session["expires_in"] = datetime.now().timestamp() + token_info["expires_in"]
        return redirect("/profile")
    return jsonify({"error": "Failed to get access token"}), 400


@app.route("/spotifytoken")
@login_required
def spotifytoken():
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_SECRET,
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code == 200:
        token_info = response.json()
        session["access_token"] = token_info["access_token"]
        session["expires_in"] = datetime.now().timestamp() + token_info["expires_in"]
        return jsonify(
            {"message": "Token retrieved successfully", "token_info": token_info}
        )
    return jsonify({"error": "Failed to get access token"}), 400


@app.route("/playlists")
@login_required
@active_spotify_session_required
def playlists():
    playlist_id = request.args.get("playlist_id", "2vZX9OzU7tcqCt6TC4ZECE")
    PLAYLIST_URL = f"{API_BASE_URL}/playlists/{playlist_id}"
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    response = requests.get(PLAYLIST_URL, headers=headers)
    if response.status_code == 200:
        playlist_data = response.json()
        return jsonify(playlist_data)
    return jsonify({"error": "Failed to get playlist data"}), 400


@app.route("/playlists/tracks")
@login_required
@active_spotify_session_required
def playlists_tracks():
    playlist_id = request.args.get("playlist_id", "2vZX9OzU7tcqCt6TC4ZECE")
    limit = request.args.get("limit", 10)
    offset = request.args.get("offset", 0)
    PLAYLIST_TRACKS_URL = f"{API_BASE_URL}/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    params = {
        "limit": limit,
        "offset": offset,
    }
    response = requests.get(PLAYLIST_TRACKS_URL, headers=headers, params=params)
    if response.status_code == 200:
        tracks_data = response.json()
        return jsonify(tracks_data)
    return jsonify({"error": "Failed to get playlist tracks data"}), 400


@app.route("/me/player", methods=["GET"])
@login_required
@active_spotify_session_required
def get_current_playback():
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }

    response = requests.get(f"{API_BASE_URL}/me/player", headers=headers)

    if response.status_code == 200:
        playback_data = response.json()
        return jsonify(playback_data)
    return jsonify({"error": "Failed to get current playback data"}), 400


@app.route("/me/player", methods=["PUT"])
def transfer_playback():
    device_id = request.args.get("device_id")
    play = request.args.get("play", "false").lower() == "true"
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
        "Content-Type": "application/json",
    }
    data = {
        "device_ids": [device_id],
        "play": play,
    }

    response = requests.put(f"{API_BASE_URL}/me/player", headers=headers, json=data)
    if response.status_code == 204:
        return jsonify({"message": "Playback transferred successfully"})
    return jsonify({"error": "Failed to transfer playback"}), 400


@app.route("/me/player/devices", methods=["GET"])
@login_required
@active_spotify_session_required
def get_available_devices():
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    response = requests.get(f"{API_BASE_URL}/me/player/devices", headers=headers)
    if response.status_code == 200:
        devices_data = response.json()
        return jsonify(devices_data)
    return jsonify({"error": "Failed to get available devices"}), 400


@app.route("/me/player/currently-playing", methods=["GET"])
@login_required
@active_spotify_session_required
def get_currently_playing_track():
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    response = requests.get(
        f"{API_BASE_URL}/me/player/currently-playing", headers=headers
    )
    if response.status_code == 200:
        track_data = response.json()
        return jsonify(track_data)
    return jsonify({"error": "Failed to get currently playing track"}), 400


@app.route("/me/player/play", methods=["PUT"])
@login_required
@active_spotify_session_required
def start_playback():
    device_id = request.args.get("device_id")
    context_uri = request.json.get("context_uri")
    uris = request.json.get("uris")
    offset = request.json.get("offset", 0)
    position = request.json.get("position", 0)

    headers = {
        "Authorization": f"Bearer {session['access_token']}",
        "Content-Type": "application/json",
    }
    params = {"device_id": device_id}
    data = {
        "context_uri": context_uri,
        "uris": uris,
        "offset": {"position": offset},
        "position_ms": position,
    }

    response = requests.put(
        f"{API_BASE_URL}/me/player/play",
        headers=headers,
        params=params,
        json=data,
    )
    if response.status_code == 204:
        return jsonify({"message": "Playback started successfully"})
    return jsonify({"error": "Failed to start playback"}), 400


@app.route("/me/player/pause", methods=["PUT"])
@login_required
@active_spotify_session_required
def pause_playback():
    device_id = request.args.get("device_id")
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    params = {"device_id": device_id}
    response = requests.put(
        f"{API_BASE_URL}/me/player/pause", headers=headers, params=params
    )
    if response.status_code == 204:
        return jsonify({"message": "Playback paused successfully"})
    return jsonify({"error": "Failed to pause playback"}), 400


@app.route("/me/player/next", methods=["POST"])
@login_required
@active_spotify_session_required
def skip_to_next_track():
    device_id = request.args.get("device_id")
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    params = {
        "device_id": device_id,
    }
    response = requests.post(
        f"{API_BASE_URL}/me/player/next",
        headers=headers,
        params=params,
    )
    if response.status_code == 204:
        return jsonify({"message": "Skipped to next track successfully"})
    return jsonify({"error": "Failed to skip to next track"}), 400


@app.route("/me/player/previous", methods=["POST"])
@login_required
@active_spotify_session_required
def skip_to_previous_track():
    device_id = request.args.get("device_id")
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    params = {
        "device_id": device_id,
    }
    response = requests.post(
        f"{API_BASE_URL}/me/player/previous",
        headers=headers,
        params=params,
    )
    if response.status_code == 204:
        return jsonify({"message": "Skipped to previous track successfully"})
    return jsonify({"error": "Failed to skip to previous track"}), 400


@app.route("/me/player/seek", methods=["PUT"])
@login_required
@active_spotify_session_required
def seek_to_position():
    device_id = request.args.get("device_id")
    position_ms = request.json.get("position_ms")
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    params = {
        "position_ms": position_ms,
        "device_id": device_id,
    }

    response = requests.put(
        f"{API_BASE_URL}/me/player/seek",
        headers=headers,
        params=params,
    )

    if response.status_code == 204:
        return jsonify({"message": "Seeked to position successfully"})
    return jsonify({"error": "Failed to seek to position"}), 400


@app.route("/me/player/repeat", methods=["PUT"])
@login_required
@active_spotify_session_required
def set_repeat_mode():
    device_id = request.args.get("device_id")
    state = request.json.get("state")
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    params = {
        "state": state,
        "device_id": device_id,
    }

    response = requests.put(
        f"{API_BASE_URL}/me/player/repeat",
        headers=headers,
        params=params,
    )

    if response.status_code == 204:
        return jsonify({"message": "Repeat mode set successfully"})
    return jsonify({"error": "Failed to set repeat mode"}), 400


@app.route("/me/player/shuffle", methods=["PUT"])
@login_required
@active_spotify_session_required
def toggle_shuffle():
    device_id = request.args.get("device_id")
    state = request.json.get("state")
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    params = {
        "state": state,
        "device_id": device_id,
    }

    response = requests.put(
        f"{API_BASE_URL}/me/player/shuffle",
        headers=headers,
        params=params,
    )
    if response.status_code == 204:
        return jsonify({"message": "Shuffle mode toggled successfully"})
    return jsonify({"error": "Failed to toggle shuffle mode"}), 400


@app.route("/me/player/recently-played", methods=["GET"])
@login_required
@active_spotify_session_required
def get_recently_played_tracks():
    limit = request.args.get("limit", 10)
    after = request.args.get("after")
    before = request.args.get("before")
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    params = {
        "limit": limit,
        "after": after,
        "before": before,
    }

    response = requests.get(
        f"{API_BASE_URL}/me/player/recently-played",
        headers=headers,
        params=params,
    )
    if response.status_code == 200:
        tracks_data = response.json()
        return jsonify(tracks_data)
    return jsonify({"error": "Failed to get recently played tracks"}), 400


@app.route("/me/player/queue", methods=["GET"])
@login_required
@active_spotify_session_required
def get_users_queue():
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }

    response = requests.get(
        f"{API_BASE_URL}/me/player/queue",
        headers=headers,
    )

    if response.status_code == 200:
        queue_data = response.json()
        return jsonify(queue_data)
    return jsonify({"error": "Failed to get user's queue"}), 400


@app.route("/me/player/queue", methods=["POST"])
@login_required
@active_spotify_session_required
def add_item_to_queue():
    uri = request.json.get("uri")
    device_id = request.args.get("device_id")
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    params = {"uri": uri, "device_id": device_id}
    response = requests.post(
        f"{API_BASE_URL}/me/player/queue", headers=headers, params=params
    )

    if response.status_code == 204:
        return jsonify({"message": "Item added to queue successfully"})
    return jsonify({"error": "Failed to add item to queue"}), 400


@app.route("/me", methods=["GET"])
@login_required
@active_spotify_session_required
def get_current_users_profile():
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }
    response = requests.get(
        f"{API_BASE_URL}/me",
        headers=headers,
    )

    if response.status_code == 200:
        user_data = response.json()
        return jsonify(user_data)
    return jsonify({"error": "Failed to get user's profile"}), 400


@app.route("/playlists/tracks", methods=["POST"])
@login_required
@active_spotify_session_required
def add_tracks_to_playlist():
    playlist_id = request.args.get("playlist_id")
    uris = request.json.get("uris")
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{API_BASE_URL}/playlists/{playlist_id}/tracks",
        headers=headers,
        data={"uris": uris},
    )

    if response.status_code == 201:
        return jsonify({"message": "Tracks added to playlist successfully"})
    return jsonify({"error": "Failed to add tracks to playlist"}), 400


@app.route("/artists", methods=["GET"])
@login_required
@active_spotify_session_required
def get_artist():
    artist_id = request.args.get("artist_id")
    headers = {
        "Authorization": f"Bearer {session['access_token']}",
    }

    response = requests.get(
        f"{API_BASE_URL}/artists/{artist_id}",
        headers=headers,
    )

    if response.status_code == 200:
        artist_data = response.json()
        return jsonify(artist_data)
    return jsonify({"error": "Failed to get artist data"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
