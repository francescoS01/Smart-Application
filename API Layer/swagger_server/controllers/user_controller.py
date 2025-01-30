"""
    This module contains methods that handle REST API requests related to users and authentication.
"""
import connexion
import six
import requests
import flask

from swagger_server.models.authentication_info import AuthenticationInfo  # noqa: E501
from swagger_server.models.id import ID  # noqa: E501
from swagger_server.models.user_basic_info import UserBasicInfo  # noqa: E501
from swagger_server.models.user_not_found_error import UserNotFoundError  # noqa: E501
from swagger_server.models.user_role import UserRole  # noqa: E501
from swagger_server import util
from swagger_server.utils.header_parameters import ParameterFormatter
from swagger_server.utils import db_retrieval

SECURITYSERVICE = 'flask-app'
PORT = '5000'
SECURITYURL = 'http://'+SECURITYSERVICE+':'+PORT
TIMEOUT = 60

def user_get():  # noqa: E501
    """Returns user informations

    Returns the informations of the connected user # noqa: E501


    :rtype: UserBasicInfo
    """
    user_info = connexion.context['token_info']['user']
    # remove user id and password
    user_info.pop('id', None)
    user_info.pop('password', None)
    return user_info, 200


def user_id_delete(id):  # noqa: E501
    """[Unimplemented] Deletes a user

    Deletes the user given its id # noqa: E501

    :param id: ID of the resource
    :type id: dict | bytes

    :rtype: str
    """
    return "unimplemented", 501


def user_id_get(id):  # noqa: E501
    """[Unimplemented] Returns user informations

    Returns informations of a user given their id # noqa: E501

    :param id: ID of the resource
    :type id: dict | bytes

    :rtype: UserBasicInfo
    """
    return "unimplemented", 501


def user_id_put(id, username=None, email=None, first_name=None, last_name=None, password=None, role=None):  # noqa: E501
    """[Unimplemented] Updates a user account

    Updates informations of a user # noqa: E501

    :param id: ID of the resource
    :type id: dict | bytes
    :param username: 
    :type username: str
    :param email: 
    :type email: str
    :param first_name: 
    :type first_name: str
    :param last_name: 
    :type last_name: str
    :param password: 
    :type password: str
    :param role: The role of the user to add
    :type role: dict | bytes

    :rtype: None
    """
    return "unimplemented", 501


def user_login_post():  # noqa: E501
    """Logs user into the system

    Attempts to log a user into the system given with their credentials. On success, returns a token that is needed in the &#x27;Authorization&#x27; header of protected API calls. The token has a TTL. # noqa: E501

    :param username: The username for login
    :type username: str
    :param password: The password for login in clear text
    :type password: str

    :rtype: AuthenticationInfo
    """
    # Parse parameters
    try:
        username = ParameterFormatter(connexion.request, 'username').as_string()
        password = ParameterFormatter(connexion.request, 'password').as_string()
    except:
        return 'Invalid parameters', 400

    data = {
        'username': username,
        'password': password
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(SECURITYURL+'/login', json=data, headers=headers, timeout=TIMEOUT, verify=False)
        response_body = response.json()
        if response.status_code != 200:
            return response_body, response.status_code
        return f"Bearer {response_body['token']}", 200
    except Exception as e:
        print(e)
        return 'Security service error', 500
    


def user_logout_get():  # noqa: E501
    """Logs out current user

    Logs out current user, invalidating their authentication token. # noqa: E501


    :rtype: str
    """
    token = connexion.context['token_info']['token'].split(' ')[1]
    
    data = {
        'token': token
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(SECURITYURL+'/logout', json=data, headers=headers, timeout=TIMEOUT, verify=False)
        if response.status_code != 200:
            return response.json(), response.status_code
        return 'Logged out', 200
    except:
        return 'Security service error', 500

def user_post():  # noqa: E501
    """Registers a new user account

    Registers a new user account and returns the id of the new account in the response body if successful. # noqa: E501

    :param username: A username for subsequent access
    :type username: str
    :param email: Email of the user
    :type email: str
    :param first_name: Name of the user
    :type first_name: str
    :param last_name: Surname of the user
    :type last_name: str
    :param password: Password of the user for subsequent access
    :type password: str
    :param role: Role of the user
    :type role: dict | bytes

    :rtype: ID
    """
    # Parse parameters
    try:
        username = ParameterFormatter(connexion.request, 'username').as_string()
        email = ParameterFormatter(connexion.request, 'email').as_string()
        firstName = ParameterFormatter(connexion.request, 'firstName').as_string()
        lastName = ParameterFormatter(connexion.request, 'lastName').as_string()
        password = ParameterFormatter(connexion.request, 'password').as_string()
        role = ParameterFormatter(connexion.request, 'role').as_string()
    except:
        return 'Invalid parameters', 400
    
    if None in [username, email, firstName, lastName, password, role]:
        return 'Invalid parameters', 400
    
    data = {
        'username': username,
        'email': email,
        'name': firstName,
        'surname': lastName,
        'password': password,
        'role': role
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(SECURITYURL+'/users', json=data, headers=headers, timeout=TIMEOUT, verify=False)
        response_body = response.json()
        if response.status_code != 201:
            return response_body, response.status_code
        return response_body['id'], 201
    except:
        return 'Security service error', 500
    
