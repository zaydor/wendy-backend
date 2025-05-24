import os

import pyrebase


class FirebaseHelper:
    _instance = None
    _auth = None
    _db = None

    @staticmethod
    def get_instance():
        if FirebaseHelper._instance is None:
            FirebaseHelper._instance = FirebaseHelper()
        return FirebaseHelper._instance

    def __init__(self):
        if FirebaseHelper._instance is not None:
            raise Exception("This class is a singleton!")
        FirebaseHelper._instance = self

    def initialize(self):
        config = {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", None),
            "serviceAccount": os.getenv("FIREBASE_SERVICE_ACCOUNT", None),
        }
        firebase = pyrebase.initialize_app(config)
        self._auth = firebase.auth()
        self._db = firebase.database()

    @property
    def auth(self):
        return self._auth

    @property
    def db(self):
        return self._db
