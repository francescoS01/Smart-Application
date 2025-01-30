from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis

app = Flask(__name__)

# Connect to Redis
redis_client = Redis(host='localhost', port=6379)

# Rate Limiter (5 requests per minute) using Redis
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="redis://localhost:6379"  # Redis connection string
)


@app.route("/validate-token", methods=["POST", "GET"])
@limiter.limit("5 per minute")
def validate_token_endpoint():
    auth_header = request.headers.get("Authorization")
    if not auth_header or "Bearer " not in auth_header:
        return jsonify({"message": "Token missing or malformed"}), 400
    token = auth_header.split("Bearer ")[1]

    # Simulate token validation (replace with actual logic)
    is_valid = token == "example_token"  # Replace with real validation logic
    if is_valid:
        return jsonify({"message": "Token valid", "user_id": 1}), 200
    else:
        return jsonify({"message": "Invalid or expired token"}), 401

if __name__ == "__main__":
    app.run(debug=True)


