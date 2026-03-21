import os
from functools import wraps

from flask import jsonify, session
from google_auth_oauthlib.flow import Flow

OAUTH_REDIRECT_URI = os.getenv(
    "OAUTH_REDIRECT_URI", "http://localhost:5000/api/auth/google/callback"
)
if OAUTH_REDIRECT_URI == "localhost" or OAUTH_REDIRECT_URI == "127.0.0.1":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def init_oauth_client(redirect_uri=None):
    uri = redirect_uri or OAUTH_REDIRECT_URI
    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [uri],
        }
    }
    scopes = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]
    flow = Flow.from_client_config(client_config, scopes=scopes, redirect_uri=uri)
    return flow


def require_user_auth(f):
    @wraps(f)
    def wrapped_method(*args, **kwargs):
        if "user_id" in session:
            from app import deps

            kwargs["user_id"] = session["user_id"]
            user = deps.db.get_user_by_id(session["user_id"])
            if user:
                session["user_type"] = user.get("user_type", "regular")
        elif DEV_AUTH_BYPASS:
            kwargs["user_id"] = "dev-user-bypass"
        else:
            return jsonify({"error": "Unauthorized", "message": "Please log in"}), 401
        return f(*args, **kwargs)

    return wrapped_method


def is_dev_auth_bypassed():
    redirect_to_localhost = (
        "localhost" in OAUTH_REDIRECT_URI or "127.0.0.1" in OAUTH_REDIRECT_URI
    )

    dev_auth_bypass = os.getenv("DEV_AUTH_BYPASS", "False").lower() == "true"
    in_development = os.getenv("FLASK_ENV") == "development"
    return redirect_to_localhost and dev_auth_bypass and in_development


DEV_AUTH_BYPASS = is_dev_auth_bypassed()
