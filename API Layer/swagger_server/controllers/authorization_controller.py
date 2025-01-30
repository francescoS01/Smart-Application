"""
controller generated to handle auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""
from swagger_server.utils import authentication_utils
import requests

SECURITYSERVICE = 'flask-app'
PORT = '5000'
SECURITYURL = 'http://'+SECURITYSERVICE+':'+PORT
TIMEOUT = 60


def check_api_token_auth(token):
    """
    Check if the token is valid and return the user information if it is
    """
    try:
        response = requests.post(SECURITYURL + '/validate-token', json={'token': token}, timeout=TIMEOUT)
        if response.status_code != 200:
            return None
        return {'token': token, 'user': response.json()}
    except Exception as e:
        return None
    
# not used
def check_machine_auth(token):
    return {'scopes': ['read:pets', 'write:pets'], 'uid': 'test_value'}

# not used
def validate_scope_machine_auth(required_scopes, token_scopes):
    return set(required_scopes).issubset(set(token_scopes))


