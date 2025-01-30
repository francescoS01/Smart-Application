from flask import Flask, request, jsonify
import requests
from authentication_db import (
    authorize_user_and_get_token,
    authorize_user_by_token,
    get_user_by_token,
    add_user,
    update_user,
    remove_user,
    logout_user,
)

app = Flask(__name__) # Initialize the Flask application

# Endpoint for user login
@app.route("/login", methods=["POST"])
def login():
    # Extract the username and password from the request body
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
     # Generate a token if the user credentials are valid
    token = authorize_user_and_get_token(username, password)
    if not token: # If the credentials are invalid, return an error
        return jsonify({"message": "Invalid credentials"}), 401
    # Return the token if login is successful
    return jsonify({"token": token}), 200

# Endpoint to validate a token
@app.route("/validate-token", methods=["POST"])
# Extract the token from the request body
def validate_token():
    token = request.json.get("token")
     # Check if the token is valid or expired
    if not authorize_user_by_token(token):
        return jsonify({"message": "Invalid token"}), 401
    user = get_user_by_token(token)
    if user is None:
        return jsonify({"message": "User not found"}), 500# strange
     # Return success if the token is valid
    return jsonify(user), 200

# Endpoint to create a new user
@app.route("/users", methods=["POST"])
def create_user():
    # Extract user details from the request body
    data = request.json
    username = data.get("username")
    # Add the user to the database and return their user ID
    user_id = add_user(
        username=username,
        password=data.get("password"),
        email=data.get("email"),
        name=data.get("name"),
        surname=data.get("surname"),
        role=data.get("role"),
    )
    return jsonify({"id": user_id}), 201 # Return the new user's ID with a 201 status

# Endpoint to update an existing user's information
@app.route("/users/<username>", methods=["PUT"])
def edit_user(username):
    # Update user details based on the provided username
    user = update_user(username, **request.json)
     # If the user doesn't exist, return a 404 error
    if not user:
        return jsonify({"message": "User not found"}), 404
    # Return the updated user details
    return jsonify(user), 200

# Endpoint to delete a user
@app.route("/users/<username>", methods=["DELETE"])
def delete_user(username):
    # Remove the user from the database
    if not remove_user(username):
        return jsonify({"message": "User not found"}), 404  # Return an error if the user isn't found
    
    # Confirm the user was deleted
    return jsonify({"message": "User deleted"}), 200


# Endpoint to log out a user
@app.route("/logout", methods=["POST"])
def logout():
    # Extract the token from the request body
    token = request.json.get("token")
    # Log out the user by invalidating their token
    if not logout_user(token):
        return jsonify({"message": "Invalid token"}), 400 # Return an error if the token is invalid
    
    # Confirm the user was logged out
    return jsonify({"message": "Logged out successfully"}), 200

# Host and port for making external API requests
API_HOST = "api-layer"
API_PORT = 443

# Helper function to make API requests
def make_api_request(endpoint):
    # Construct the URL using the host, port, and endpoint
    url = f"https://{API_HOST}:{API_PORT}/{endpoint}"
    
    # Send a GET request to the external API and return the JSON response
    response = requests.get(url)
    return response.json()

# Main entry point for running the Flask application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) # Run the app on port 5000
    # app.run(debug=True) # Uncomment for debugging during development

