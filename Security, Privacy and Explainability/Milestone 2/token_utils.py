import bcrypt
import secrets
import jwt
from datetime import datetime, timedelta
from db_utils import get_db_connection

# Secret key for signing JWTs (stored securely in .env file)
SECRET_KEY = "secret_key"

def generate_token(user_id, token_type="uuid"):
    expiration_time = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour

    if token_type == "uuid":
        # Generate a random UUID-based token
        token = secrets.token_urlsafe(32)
    elif token_type == "jwt":
        # Generate a JWT
        token = jwt.encode(
            {"user_id": user_id, "exp": expiration_time},
            SECRET_KEY,
            algorithm="HS256",
        )
    else:
        raise ValueError("Invalid token type")

    # Hash the token before storing it in the database
    token_hash = bcrypt.hashpw(token.encode(), bcrypt.gensalt()).decode()

    return token, token_hash, expiration_time

def validate_token(token):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Query the database for a matching token hash
            cur.execute("SELECT * FROM tokens WHERE expiration > NOW()")
            tokens = cur.fetchall()

            for db_token in tokens:
                if bcrypt.checkpw(token.encode(), db_token["token_hash"].encode()):
                    return True, db_token["user_id"]

        return False, None
    finally:
        conn.close()
