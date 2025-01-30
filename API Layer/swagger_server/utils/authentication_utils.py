"""
    Authentication utilities
"""

import random
from datetime import datetime, timedelta

TOKEN_VALIDITY = 5 # minutes
mock_auth_db = {
    "users": {
        "mario.rossi": {
            "password": "password1",
            "email": "mario.rossi@gmail.com",
            "name": "Mario",
            "surname": "Rossi",
            "role": "SMO",
            "username": "mario.rossi",
            "id": 1
        },
        "luigi.bianchi": {
            "password": "password2",
            "email": "luigi.bianchi@gmail.com",
            "name": "Luigi",
            "surname": "Bianchi",
            "role": "FFM",
            "username": "luigi.bianchi",
            "id": 2
        },
        "RAG": {
            "password": "password3",
            "email": None,
            "name": None,
            "surname": None,
            "role": "System",
            "username": "RAG",
            "id": 3
        },
        "KPIENGINE": {
            "password": "password4",
            "email": None,
            "name": None,
            "surname": None,
            "role": "System",
            "username": "KPIENGINE",
            "id": 4
        },
        "PREPROCESSING": {
            "password": "password5",
            "email": None,
            "name": None,
            "surname": None,
            "role": "System",
            "username": "PREPROCESSING",
            "id": 5
        }
    },
    "tokens": {
        "token1": {
            "user": "mario.rossi",
            "expiration": "2021-12-31T23:59:59Z"
        },
        "test_token": {
            "user": "RAG",
            "expiration": "2024-12-31T23:59:59Z"
        },
    }
}

# get user by id
def get_user(id):
    """
        Get user informations by id

        :param id: The id of the user
        :type id: int

        :return: The user informations
        :rtype: dict
    """
    return mock_auth_db["users"].get(id)

# get user by token
def get_user_by_token(token):
    """
        Get user informations by token

        :param token: The token of the user
        :type token: str

        :return: The user informations
        :rtype: dict
    """
    user = mock_auth_db["tokens"].get(token)
    if user is None:
        return None
    user = user["user"]
    return get_user(user)

# authorize user by username and password and return token
def authorize_user_and_get_token(username, password):
    """
        Authorize user by username and password and return a newly generated token

        :param username: The username of the user
        :type username: str
        :param password: The password of the user
        :type password: str

        :return: The token of the user
        :rtype: str
    """
    user_to_check = mock_auth_db["users"].get(username)
    password_to_check = user_to_check.get("password")
    if password_to_check != password:
        return None
    # generate token
    token = "token" + str(random.randint(1, 1000))
    mock_auth_db["tokens"][token] = {
        "user": username,
        "expiration": (datetime.now() + timedelta(minutes=TOKEN_VALIDITY)).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    return token

# check if token is valid
def is_token_valid(token):
    """
        Check if token is valid

        :param token: The token of the user
        :type token: str

        :return: True if token is valid, False otherwise
        :rtype: bool
    """
    token_data = mock_auth_db["tokens"].get(token)
    if token_data is None:
        return False
    expiration = datetime.strptime(token_data["expiration"], "%Y-%m-%dT%H:%M:%SZ")
    if expiration <= datetime.now():
        # remove expired token
        mock_auth_db["tokens"].pop(token)
        return False
    return True

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
    mock_auth_db["tokens"][token]["expiration"] = (datetime.now() + timedelta(minutes=TOKEN_VALIDITY)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return True

# add user to db and return user id
def add_user(username, password, email, name, surname, role):
    """
        Add user to db and return user id

        :param username: The username of the user
        :type username: str
        :param password: The password of the user
        :type password: str
        :param email: The email of the user
        :type email: str
        :param name: The name of the user
        :type name: str
        :param surname: The surname of the user
        :type surname: str
        :param role: The role of the user
        :type role: str

        :return: The id of the user
        :rtype: int
    """
    user_id = max([user["id"] for user in mock_auth_db["users"].values()]) + 1
    mock_auth_db["users"][username] = {
        "password": password,
        "email": email,
        "name": name,
        "surname": surname,
        "role": role,
        "username": username,
        "id": user_id
    }
    return user_id

# remove user from db
def remove_user(username):
    """
        Remove user from db

        :param username: The username of the user
        :type username: str

        :return: True if user is removed, False if user is not found
        :rtype: bool
    """
    user = mock_auth_db["users"].pop(username)
    if user is None:
        return False
    return True

# update user in db
def update_user(id, username=None, password=None, email=None, name=None, surname=None, role=None):
    """
        Update user in db

        :param id: The id of the user
        :type id: int
        :param username: The username of the user
        :type username: str
        :param password: The password of the user
        :type password: str
        :param email: The email of the user
        :type email: str
        :param name: The name of the user
        :type name: str
        :param surname: The surname of the user
        :type surname: str
        :param role: The role of the user
        :type role: str

        :return: The updated user informations
        :rtype: dict
    """
    user = mock_auth_db["users"].get(id)
    if user is None:
        return None
    if username is not None:
        user["username"] = username
    if password is not None:
        user["password"] = password
    if email is not None:
        user["email"] = email
    if name is not None:
        user["name"] = name
    if surname is not None:
        user["surname"] = surname
    if role is not None:
        user["role"] = role
    return user

# invalidate token
def logout_user(token):
    """
        Invalidate token

        :param token: The token of the user
        :type token: str

        :return: True if token is invalidated, False if token is not found
        :rtype: bool
    """
    res = mock_auth_db["tokens"].pop(token)
    if res is None:
        return False
    return True
