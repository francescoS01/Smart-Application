import requests
import os

# load the correct host name from the environment if defined
HOSTNAME = os.getenv('API_HOSTNAME', 'localhost')
PORT = 443
BASE_URL = f'https://{HOSTNAME}:{PORT}'

YOUR_USERNAME = 'sysadmin'# change this, until topic 7 gives you real credentials anything will work
YOUR_PASSWORD = 'sysadmin'# change this, until topic 7 gives you real credentials anything will work

#########################################
AUTH_URL = f'{BASE_URL}/user/login'

auth_token = None

def get_token(url, username, password):
    headers = {
        'username': username,
        'password': password
    }  
    response = requests.post(url, headers=headers, verify=False)
    if response.status_code == 200:
        print('You are authenticated!')
        return response.json()
    elif response.status_code == 400:
        print('Wrong credentials')
    elif response.status_code == 500:
        print('Connection error')
    else:
        print('Unknown error')
    return None

auth_token = get_token(AUTH_URL, YOUR_USERNAME, YOUR_PASSWORD)
print('Token: ', auth_token)

##########################

def call_with_token(url, token, call_type='GET', header_params=None):
    headers = {} if header_params is None else header_params
    headers['Authorization'] = token
    if call_type == 'GET':
        response = requests.get(url, headers=headers, verify=False)
    elif call_type == 'POST':
        response = requests.post(url, headers=headers, verify=False)
    elif call_type == 'PUT':
        response = requests.put(url, headers=headers, verify=False)
    elif call_type == 'DELETE':
        response = requests.delete(url, headers=headers, verify=False)
    else:
        print('Unknown call type')
        return None, None
    if response.status_code == 500:
        print('Server error: ', response.reason)
        return None, response.status_code
    elif response.status_code == 400:
        print('Bad request: ', response.reason)
        return None, response.status_code
    elif response.status_code == 401:
        print('Unauthorized')
        return None, response.status_code
    elif response.status_code == 200:
        return response.json(), response.status_code
    else:
        print('Unknown error: ', response.reason)
        return None, response.status_code


def call_and_retry(url, token, call_type='GET', header_params=None):
    response, status = call_with_token(url, token, call_type, header_params)
    if status == 401:
        print('Token expired, getting new token')
        token = get_token(AUTH_URL, YOUR_USERNAME, YOUR_PASSWORD)
        if token is None:
            print('Failed to get new token')
            return None, 401
        return call_and_retry(url, token, call_type, header_params)
    return response, status


#########################################

# Function to construct and send alerts dynamically
def send_alert(machineID, severity, description, kpi, aggr_type, label, timestamp=None):
    """
    Send an alert with specified parameters.
    
    Args:
        machineID (str): Identifier for the machine.
        severity (str): Alert severity (e.g., 'low', 'medium', 'high').
        description (str): Description of the alert.
        kpi (str): KPI associated with the alert.
        aggr_type (str): Aggregation type of the KPI (e.g., 'daily', 'hourly').
        label (str): The label or category of the alert.
        timestamp (str): Optional timestamp for the alert. If not provided, use the current time.
    """
    import datetime
    # Default to the current timestamp if not provided
    if timestamp is None:
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    # Construct the alert data
    alert_data = {
        "timestamp": timestamp,
        "machineID": machineID,
        "severity": severity,
        "description": description,
        "KPI": kpi,
        "aggr_type": aggr_type,
        "label": label
    }

    # Send the alert
    endpoint_url = f'{BASE_URL}/alert'
    response, status = call_and_retry(endpoint_url, auth_token, call_type='POST', header_params=alert_data)
    if status == 200:
        print(f'Alert successfully sent: {alert_data}')
    else:
        print(f'Failed to send alert: {alert_data} with status code {status}')
