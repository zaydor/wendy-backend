import os
from datetime import datetime

import requests
from flask import Blueprint, jsonify, request, session
from helpers import FirebaseHelper, active_spotify_session_required, login_required
from models import (
    AuthUrlResponse,
    ErrorResponse,
    Playlist,
    PlaylistResponse,
    StandardResponse,
    TokenInfoResponse,
)


class SpotifyRoutes:
    def __init__(self):
        self.spotify_bp = Blueprint("spotify", __name__)
        self.SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
        self.SPOTIFY_SECRET = os.getenv("SPOTIFY_SECRET")
        self.REDIRECT_URI = "http://127.0.0.1/callback"
        self.AUTH_URL = "https://accounts.spotify.com/authorize"
        self.TOKEN_URL = "https://accounts.spotify.com/api/token"
        self.API_BASE_URL = "https://api.spotify.com/v1"
        self.register_routes()

    def register_routes(self):
        bp = self.spotify_bp

        @bp.route("/authorize")
        @login_required
        def authorize():
            redirect_uri = request.args.get("redirect_uri", self.REDIRECT_URI)
            scope = "user-read-private user-read-email user-read-playback-state user-modify-playback-state playlist-read-private user-read-recently-played user-read-currently-playing playlist-modify-public playlist-modify-private"
            params = {
                "client_id": self.SPOTIFY_CLIENT_ID,
                "response_type": "code",
                "redirect_uri": redirect_uri,
                "scope": scope,
            }
            response = requests.get(self.AUTH_URL, params=params)
            auth_url = response.url
            print(f"{response=}")
            return AuthUrlResponse(auth_url=auth_url).build()

        @bp.route("/callback")
        def callback():
            code = request.args.get("code")
            redirect_uri = request.args.get("redirect_uri", self.REDIRECT_URI)
            auth_options = {
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
            response = requests.post(
                self.TOKEN_URL,
                data=auth_options,
                auth=(self.SPOTIFY_CLIENT_ID, self.SPOTIFY_SECRET),
            )
            print(f"{response.json()=}")
            print(f"{session.keys()=}")
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
                return StandardResponse(
                    message="Access token retrieved successfully"
                ).build()
            return ErrorResponse(error="Failed to get access token").build()

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
                return TokenInfoResponse(
                    message="Access token retrieved successfully",
                    token_info=token_info,
                ).build()
            return ErrorResponse(error="Failed to get access token").build()

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
                # TODO
                playlist_data = response.json()
                playlist = Playlist()
                return PlaylistResponse(playlist=playlist).build()
            return ErrorResponse(error="Failed to get playlist data").build()

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
                # TODO
                tracks_data = response.json()
                return jsonify(tracks_data)
            return ErrorResponse(error="Failed to get playlist tracks data").build()

        @bp.route("/me/player", methods=["GET"])
        @login_required
        @active_spotify_session_required
        def get_current_playback():
            headers = {
                "Authorization": f"Bearer {session['access_token']}",
            }
            response = requests.get(f"{self.API_BASE_URL}/me/player", headers=headers)
            if response.status_code == 200:
                # TODO
                playback_data = response.json()
                return jsonify(playback_data)
            return ErrorResponse(error="Failed to get current playback data").build()

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
                return StandardResponse(
                    message="Playback transferred successfully", status=204
                ).build()
            return ErrorResponse(error="Failed to transfer playback").build()

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
                # TODO
                devices_data = response.json()
                return jsonify(devices_data)
            return ErrorResponse(error="Failed to get available devices").build()

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
                # TODO
                track_data = response.json()
                return jsonify(track_data)
            return ErrorResponse(
                error="Failed to get currently playing track",
            ).build()

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
                return StandardResponse(
                    message="Playback started successfully", status=204
                ).build()
            return ErrorResponse(error="Failed to start playback").build()

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
                return StandardResponse(
                    message="Playback paused successfully", status=204
                ).build()
            return ErrorResponse(error="Failed to pause playback").build()

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
                return StandardResponse(
                    message="Skipped to next track successfully", status=204
                ).build()
            return ErrorResponse(error="Failed to skip to next track").build()

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
                return StandardResponse(
                    message="Skipped to previous track successfully", status=204
                ).build()
            return ErrorResponse(error="Failed to skip to previous track").build()

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
                return StandardResponse(
                    message="Seeked to position successfully", status=204
                ).build()
            return ErrorResponse(error="Failed to seek to position").build()

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
                return StandardResponse(
                    "Repeat mode set successfully", status=204
                ).build()
            return ErrorResponse(error="Failed to set repeat mode").build()

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
                return StandardResponse(
                    message="Shuffle mode toggled successfully", status=204
                ).build()
            return ErrorResponse(error="Failed to toggle shuffle mode").build()

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
                # TODO
                tracks_data = response.json()
                return jsonify(tracks_data)
            return ErrorResponse(error="Failed to get recently played tracks").build()

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
                # TODO
                queue_data = response.json()
                return jsonify(queue_data)
            return ErrorResponse(error="Failed to get user's queue").build()

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
                return StandardResponse(
                    message="Item added to queue successfully", status=204
                ).build()
            return ErrorResponse(error="Failed to add item to queue").build()

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
                # TODO
                user_data = response.json()
                return jsonify(user_data)
            return ErrorResponse(error="Failed to get user's profile").build()

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
                return StandardResponse(
                    message="Tracks added to playlist successfully", status=201
                ).build()
            return ErrorResponse(error="Failed to add tracks to playlist").build()

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
                # TODO
                artist_data = response.json()
                return jsonify(artist_data)
            return ErrorResponse(error="Failed to get artist data").build()
