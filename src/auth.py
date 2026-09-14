import hashlib
import hmac
import secrets
import time
from src.config import settings

COOKIE_NAME = "carepulse_session"

def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180_000).hex()
    return f"pbkdf2_sha256$180000${salt}${digest}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(rounds)).hex()
        return hmac.compare_digest(actual, expected)
    except (TypeError, ValueError):
        return False

def make_session(user_id: int) -> str:
    expires = int(time.time()) + settings.session_ttl_hours * 3600
    payload = f"{user_id}.{expires}"
    signature = hmac.new(settings.secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"

def read_session(value: str | None) -> int | None:
    if not value:
        return None
    try:
        user_id, expires, signature = value.split(".", 2)
        payload = f"{user_id}.{expires}"
        expected = hmac.new(settings.secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if int(expires) < int(time.time()) or not hmac.compare_digest(signature, expected):
            return None
        return int(user_id)
    except (TypeError, ValueError):
        return None
