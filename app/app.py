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
CORS(app, 
     supports_credentials=True,
     origins=["http://localhost:8081", "http://127.0.0.1:8081"],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

FirebaseHelper.get_instance().initialize()

app.register_blueprint(AuthRoutes().auth_bp)
app.register_blueprint(SpotifyRoutes().spotify_bp)

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(redis_url)

app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis_client
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True in production with HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = False
app.config["SESSION_COOKIE_DOMAIN"] = "localhost"
app.config["SESSION_COOKIE_PATH"] = "/"
app.config["SESSION_KEY_PREFIX"] = "wendy_session:"
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 3600  # 1 hour

app.secret_key = os.getenv("SECRET_KEY")

Session(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
