from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
import os

from helpers import FirebaseHelper
from blueprints import AuthRoutes, SpotifyRoutes

load_dotenv()

app = Flask(__name__)
CORS(app)

FirebaseHelper.get_instance().initialize()

app.register_blueprint(AuthRoutes().auth_bp)
app.register_blueprint(SpotifyRoutes().spotify_bp)

# Configure session
app.secret_key = os.getenv("SECRET_KEY")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
