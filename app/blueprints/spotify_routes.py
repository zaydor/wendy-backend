import os
from datetime import datetime

import requests
from flask import Blueprint, jsonify, redirect, request, session
from helpers import FirebaseHelper, active_spotify_session_required, login_required


class SpotifyRoutes:
    def __init__(self):
        self.spotify_bp = Blueprint("spotify", __name__)
        self.SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
        self.SPOTIFY_SECRET = os.getenv("SPOTIFY_SECRET")
        self.REDIRECT_URI = "http://localhost/callback"
        self.AUTH_URL = "https://accounts.spotify.com/authorize"
        self.TOKEN_URL = "https://accounts.spotify.com/api/token"
        self.API_BASE_URL = "https://api.spotify.com/v1"
        self.register_routes()

    def register_routes(self):
        bp = self.spotify_bp

        @bp.route("/authorize")
        @login_required
        def authorize():
            scope = "user-read-private user-read-email user-read-playback-state user-modify-playback-state playlist-read-private user-read-recently-played user-read-currently-playing playlist-modify-public playlist-modify-private"
            params = {
                "client_id": self.SPOTIFY_CLIENT_ID,
                "response_type": "code",
                "redirect_uri": self.REDIRECT_URI,
                "scope": scope,
            }
            response = requests.get(self.AUTH_URL, params=params)
            auth_url = response.url
            return redirect(auth_url)

        @bp.route("/callback")
        @login_required
        def callback():
            code = request.args.get("code")
            auth_options = {
                "code": code,
                "redirect_uri": self.REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            response = requests.post(
                self.TOKEN_URL,
                data=auth_options,
                auth=(self.SPOTIFY_CLIENT_ID, self.SPOTIFY_SECRET),
            )
            if response.status_code == 200:
                token_info = response.json()
                FirebaseHelper.get_instance().db.child("users").child(
                    session["uid"]
                ).update({"refresh_token": token_info["refresh_token"]})
                session["access_token"] = token_info["access_token"]
                session["refresh_token"] = token_info["refresh_token"]
                session["expires_in"] = (
                    datetime.now().timestamp() + token_info["expires_in"]
                )
                return redirect("/profile")
            return jsonify({"error": "Failed to get access token"}), 400

        @bp.route("/spotifytoken")
        @login_required
        def spotifytoken():
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
            }
            data = {
                "grant_type": "client_credentials",
                "client_id": self.SPOTIFY_CLIENT_ID,
                "client_secret": self.SPOTIFY_SECRET,
            }
            response = requests.post(self.TOKEN_URL, headers=headers, data=data)
            if response.status_code == 200:
                token_info = response.json()
                session["access_token"] = token_info["access_token"]
                session["expires_in"] = (
                    datetime.now().timestamp() + token_info["expires_in"]
                )
                return jsonify(
                    {
                        "message": "Token retrieved successfully",
                        "token_info": token_info,
                    }
                )
            return jsonify({"error": "Failed to get access token"}), 400

        @bp.route("/playlists")
        @login_required
        @active_spotify_session_required
        def playlists():
            playlist_id = request.args.get("playlist_id", "2vZX9OzU7tcqCt6TC4ZECE")
            PLAYLIST_URL = f"{self.API_BASE_URL}/playlists/{playlist_id}"
            headers = {
                "Authorization": f"Bearer {session['access_token']}",
            }
            response = requests.get(PLAYLIST_URL, headers=headers)
            if response.status_code == 200:
                playlist_data = response.json()
                return jsonify(playlist_data)
            return jsonify({"error": "Failed to get playlist data"}), 400

        @bp.route("/playlists/tracks")
        @login_required
        @active_spotify_session_required
        def playlists_tracks():
            playlist_id = request.args.get("playlist_id", "2vZX9OzU7tcqCt6TC4ZECE")
            limit = request.args.get("limit", 10)
            offset = request.args.get("offset", 0)
            PLAYLIST_TRACKS_URL = f"{self.API_BASE_URL}/playlists/{playlist_id}/tracks"
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

        @bp.route("/me/player", methods=["GET"])
        @login_required
        @active_spotify_session_required
        def get_current_playback():
            headers = {
                "Authorization": f"Bearer {session['access_token']}",
            }
            response = requests.get(f"{self.API_BASE_URL}/me/player", headers=headers)
            if response.status_code == 200:
                playback_data = response.json()
                return jsonify(playback_data)
            return jsonify({"error": "Failed to get current playback data"}), 400

        @bp.route("/me/player", methods=["PUT"])
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
            response = requests.put(
                f"{self.API_BASE_URL}/me/player", headers=headers, json=data
            )
            if response.status_code == 204:
                return jsonify({"message": "Playback transferred successfully"})
            return jsonify({"error": "Failed to transfer playback"}), 400

        @bp.route("/me/player/devices", methods=["GET"])
        @login_required
        @active_spotify_session_required
        def get_available_devices():
            headers = {
                "Authorization": f"Bearer {session['access_token']}",
            }
            response = requests.get(
                f"{self.API_BASE_URL}/me/player/devices", headers=headers
            )
            if response.status_code == 200:
                devices_data = response.json()
                return jsonify(devices_data)
            return jsonify({"error": "Failed to get available devices"}), 400

        @bp.route("/me/player/currently-playing", methods=["GET"])
        @login_required
        @active_spotify_session_required
        def get_currently_playing_track():
            headers = {
                "Authorization": f"Bearer {session['access_token']}",
            }
            response = requests.get(
                f"{self.API_BASE_URL}/me/player/currently-playing", headers=headers
            )
            if response.status_code == 200:
                track_data = response.json()
                return jsonify(track_data)
            return jsonify({"error": "Failed to get currently playing track"}), 400

        @bp.route("/me/player/play", methods=["PUT"])
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
                f"{self.API_BASE_URL}/me/player/play",
                headers=headers,
                params=params,
                json=data,
            )
            if response.status_code == 204:
                return jsonify({"message": "Playback started successfully"})
            return jsonify({"error": "Failed to start playback"}), 400

        @bp.route("/me/player/pause", methods=["PUT"])
        @login_required
        @active_spotify_session_required
        def pause_playback():
            device_id = request.args.get("device_id")
            headers = {
                "Authorization": f"Bearer {session['access_token']}",
            }
            params = {"device_id": device_id}
            response = requests.put(
                f"{self.API_BASE_URL}/me/player/pause", headers=headers, params=params
            )
            if response.status_code == 204:
                return jsonify({"message": "Playback paused successfully"})
            return jsonify({"error": "Failed to pause playback"}), 400

        @bp.route("/me/player/next", methods=["POST"])
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
                f"{self.API_BASE_URL}/me/player/next",
                headers=headers,
                params=params,
            )
            if response.status_code == 204:
                return jsonify({"message": "Skipped to next track successfully"})
            return jsonify({"error": "Failed to skip to next track"}), 400

        @bp.route("/me/player/previous", methods=["POST"])
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
                f"{self.API_BASE_URL}/me/player/previous",
                headers=headers,
                params=params,
            )
            if response.status_code == 204:
                return jsonify({"message": "Skipped to previous track successfully"})
            return jsonify({"error": "Failed to skip to previous track"}), 400

        @bp.route("/me/player/seek", methods=["PUT"])
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
                f"{self.API_BASE_URL}/me/player/seek",
                headers=headers,
                params=params,
            )
            if response.status_code == 204:
                return jsonify({"message": "Seeked to position successfully"})
            return jsonify({"error": "Failed to seek to position"}), 400

        @bp.route("/me/player/repeat", methods=["PUT"])
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
                f"{self.API_BASE_URL}/me/player/repeat",
                headers=headers,
                params=params,
            )
            if response.status_code == 204:
                return jsonify({"message": "Repeat mode set successfully"})
            return jsonify({"error": "Failed to set repeat mode"}), 400

        @bp.route("/me/player/shuffle", methods=["PUT"])
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
                f"{self.API_BASE_URL}/me/player/shuffle",
                headers=headers,
                params=params,
            )
            if response.status_code == 204:
                return jsonify({"message": "Shuffle mode toggled successfully"})
            return jsonify({"error": "Failed to toggle shuffle mode"}), 400

        @bp.route("/me/player/recently-played", methods=["GET"])
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
                f"{self.API_BASE_URL}/me/player/recently-played",
                headers=headers,
                params=params,
            )
            if response.status_code == 200:
                tracks_data = response.json()
                return jsonify(tracks_data)
            return jsonify({"error": "Failed to get recently played tracks"}), 400

        @bp.route("/me/player/queue", methods=["GET"])
        @login_required
        @active_spotify_session_required
        def get_users_queue():
            headers = {
                "Authorization": f"Bearer {session['access_token']}",
            }
            response = requests.get(
                f"{self.API_BASE_URL}/me/player/queue",
                headers=headers,
            )
            if response.status_code == 200:
                queue_data = response.json()
                return jsonify(queue_data)
            return jsonify({"error": "Failed to get user's queue"}), 400

        @bp.route("/me/player/queue", methods=["POST"])
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
                f"{self.API_BASE_URL}/me/player/queue", headers=headers, params=params
            )
            if response.status_code == 204:
                return jsonify({"message": "Item added to queue successfully"})
            return jsonify({"error": "Failed to add item to queue"}), 400

        @bp.route("/me", methods=["GET"])
        @login_required
        @active_spotify_session_required
        def get_current_users_profile():
            headers = {
                "Authorization": f"Bearer {session['access_token']}",
            }
            response = requests.get(
                f"{self.API_BASE_URL}/me",
                headers=headers,
            )
            if response.status_code == 200:
                user_data = response.json()
                return jsonify(user_data)
            return jsonify({"error": "Failed to get user's profile"}), 400

        @bp.route("/playlists/tracks", methods=["POST"])
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
                f"{self.API_BASE_URL}/playlists/{playlist_id}/tracks",
                headers=headers,
                json={"uris": uris},
            )
            if response.status_code == 201:
                return jsonify({"message": "Tracks added to playlist successfully"})
            return jsonify({"error": "Failed to add tracks to playlist"}), 400

        @bp.route("/artists", methods=["GET"])
        @login_required
        @active_spotify_session_required
        def get_artist():
            artist_id = request.args.get("artist_id")
            headers = {
                "Authorization": f"Bearer {session['access_token']}",
            }
            response = requests.get(
                f"{self.API_BASE_URL}/artists/{artist_id}",
                headers=headers,
            )
            if response.status_code == 200:
                artist_data = response.json()
                return jsonify(artist_data)
            return jsonify({"error": "Failed to get artist data"}), 400
