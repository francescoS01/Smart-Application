from datetime import datetime, timedelta
from random import randint

TOKEN_VALIDITY = 5  
" Token validity in minutes "


db = {
    "users": {
        "mario.rossi": {
            "password": "password1",
            "email": "mario.rossi@gmail.com",
            "name": "Mario",
            "surname": "Rossi",
            "role": "SMO",
            "username": "mario.rossi",
            "id": 1,
        },
        "luigi.bianchi": {
            "password": "password2",
            "email": "luigi.bianchi@gmail.com",
            "name": "Luigi",
            "surname": "Bianchi",
            "role": "FFM",
            "username": "luigi.bianchi",
            "id": 2,
        },
        "antonio.tonarelli": {
            "password": "password2",
            "email": "antonio.tonarelli@gmail.com",
            "name": "Antonio",
            "surname": "Tonarelli",
            "role": "FFM",
            "username": "antonio.tonarelli",
            "id": 3,
        },
        "RAG": {
            "password": "password3",
            "email": None,
            "name": None,
            "surname": None,
            "role": "System",
            "username": "RAG",
            "id": 4,
        },
        "KPIENGINE": {
            "password": "password4",
            "email": None,
            "name": None,
            "surname": None,
            "role": "System",
            "username": "KPIENGINE",
            "id": 5,
        },
        "PREPROCESSING": {
            "password": "password5",
            "email": None,
            "name": None,
            "surname": None,
            "role": "System",
            "username": "PREPROCESSING",
            "id": 6,
        },
    },
    "tokens": {},
}


" Function to retrieve a user from the database using their user ID "
def get_user_by_id(user_id):
    """" 
    Loop through all users in the "users" dictionary
    
    """
    for user in db["users"].values():
        " If the user ID matches, return the user object "
        if user["id"] == user_id:
            return user
    " Return None if no user with the given ID is found "
    return None

" Function to retrieve a user based on the token provided "
def get_user_by_token(token):
    """ Get token data from the "tokens" dictionary """
    token_data = db["tokens"].get(token)
    " If token is invalid or doesn't exist, return None "
    if not token_data:
        return None
    " Retrieve the username associated with the token "
    username = token_data["user"]
    " Return the user object associated with that username "
    return db["users"].get(username)

" Function to authorize a user and generate a token if credentials are valid "
def authorize_user_and_get_token(username, password):
    """ Look for the user in the "users" dictionary using the provided username """
    user = db["users"].get(username)
    """ If no user is found or password doesn't match, return None (authorization fails)"""
    if not user or user["password"] != password:
        return None
    " Generate a token using a random 4-digit number (faking a token generation mechanism) "
    token = f"token{randint(1000, 9999)}"
    " Save the token and associate it with the username and an expiration time "
    db["tokens"][token] = {
        "user": username,
        "expiration": (datetime.now() + timedelta(minutes=TOKEN_VALIDITY)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    " Return the generated token "
    return token

" Function to check if a given token is valid (not expired) "
def is_token_valid(token):
    """ Get the token data from the "tokens" dictionary """
    token_data = db["tokens"].get(token)
    " If token doesn't exist in the database, it's invalid "
    if not token_data:
        return False
    " Get the expiration time from the token data stored in the database "
    expiration = datetime.strptime(token_data["expiration"], "%Y-%m-%dT%H:%M:%SZ")
    " If the token is expired, remove it from the database and return False "
    if expiration <= datetime.now():
        db["tokens"].pop(token)
        return False
    " If the token is valid (not expired), return True "
    return True

" Function to add a new user to the database "
def add_user(username, password, email, name, surname, role):
    " Find the next available user ID by getting the highest existing ID and adding 1, or start at 1 if no users exist "
    user_id = max(user["id"] for user in db["users"].values()) + 1 if db["users"] else 1
    """ Add the new user to the "users" dictionary with the given details """
    db["users"][username] = {
        "id": user_id,
        "username": username,
        "password": password,
        "email": email,
        "name": name,
        "surname": surname,
        "role": role,
    }
    " Return the assigned user ID "
    return user_id

" Function to update an existing user's information "
def update_user(username, **kwargs):
    """ Look for the user in the "users" dictionary by their username """
    user = db["users"].get(username)
    " If the user doesn't exist, return None "
    if not user:
        return None
    " Loop through the keyword arguments and update the user fields with the new values "
    for key, value in kwargs.items():
        if key in user:
            user[key] = value
    " Return the updated user information "
    return user

" Function to remove a user from the database "
def remove_user(username):
    " Remove the user by their username and return True if successfully removed, otherwise False "
    return db["users"].pop(username, None) is not None

" Function to log out a user by removing their token from the database "
def logout_user(token):
    """ Remove the token from the "tokens" dictionary and return True if successfully removed, otherwise False """
    return db["tokens"].pop(token, None) is not None

# authorize user by token and refresh token expiration
def authorize_user_by_token(token):
    """
        Checks token validity and refresh token expiration

        :param token: The token of the user
        :type token: str

        :return: True if token is valid, False otherwise
        :rtype: bool
    """
    if not is_token_valid(token):
        return False
    db["tokens"][token]["expiration"] = (datetime.now() + timedelta(minutes=TOKEN_VALIDITY)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return True