import os
import json
import requests
import firebase_admin
from firebase_admin import credentials, auth, db

class FirebaseHelper:
    _instance = None
    _auth = None
    _db = None
    _api_key = None

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
        # Initialize Firebase Admin SDK
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if not service_account_json:
            raise ValueError("FIREBASE_SERVICE_ACCOUNT environment variable is required")
            
        service_account_info = json.loads(service_account_json)
        cred = credentials.Certificate(service_account_info)
        
        firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv("FIREBASE_DATABASE_URL")
        })
        
        self._auth = auth
        self._db = db.reference()
        self._api_key = os.getenv("FIREBASE_API_KEY")

    def verify_password(self, email, password):
        """Verify user credentials using Firebase Auth REST API"""
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self._api_key}"
        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Invalid credentials")

    @property
    def auth(self):
        return self._auth

    @property
    def db(self):
        return self._db
