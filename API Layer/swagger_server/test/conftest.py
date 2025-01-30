"""
Fixtures for testing the API
"""
import connexion
import pytest


flask_app = connexion.FlaskApp(__name__)
flask_app.add_api('../swagger/swagger.yaml')
flask_app.app.config['DEBUG'] = True
flask_app.app.config['TESTING'] = True

@pytest.fixture(scope='session')
def client():
    with flask_app.app.test_client() as c:
        yield c

@pytest.fixture(scope='session')
def login(client):
    headers = {'username':'luigi.bianchi', 'password':'password2'}
    response = client.post('/user/login', headers=headers)
    if response.status_code == 200:
        return response.json 
    else:
        return None
    
@pytest.fixture(scope='session')
def test_machine():
    m = {
        'machineType':'Testing Machine',
        'productionLine':0,
        'factory':'test',
        'name':'test',
        'status':'idle'
        }
    return m