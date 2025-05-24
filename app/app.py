import os

import redis
from blueprints import AuthRoutes, SpotifyRoutes
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from helpers import FirebaseHelper

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

FirebaseHelper.get_instance().initialize()

app.register_blueprint(AuthRoutes().auth_bp)
app.register_blueprint(SpotifyRoutes().spotify_bp)

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.from_url(redis_url)
app.config["SESSION_COOKIE_SAMESITE"] = "None"

app.secret_key = os.getenv("SECRET_KEY")

Session(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
