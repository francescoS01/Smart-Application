import requests
import os
import datetime
import pandas as pd

# Load the correct hostname from the environment, default to 'localhost'
HOSTNAME = os.getenv('API_HOSTNAME', 'localhost')
PORT = 443
BASE_URL = f'https://{HOSTNAME}:{PORT}'

# Placeholder credentials for login (update with real credentials when available)
YOUR_USERNAME = 'sysadmin' # username: PREPROCESSING
YOUR_PASSWORD = 'sysadmin' # password: password5

# Login endpoint for authentication
AUTH_URL = f'{BASE_URL}/user/login'

# Global variable to store the authentication token
auth_token = None

def get_token(url, username, password):
    """
    Authenticate and retrieve a token.
    
    Args:
        url (str): Authentication endpoint URL.
        username (str): Username for authentication.
        password (str): Password for authentication.

    Returns:
        str: Authentication token if successful, otherwise None.
    """
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

# Authenticate and retrieve the token
auth_token = get_token(AUTH_URL, YOUR_USERNAME, YOUR_PASSWORD)
print('Token: ', auth_token)

def call_with_token(url, token, call_type='GET', header_params=None):
    """
    Make an API call with the provided token and handle responses.

    Args:
        url (str): API endpoint URL.
        token (str): Authentication token.
        call_type (str): HTTP method ('GET', 'POST', 'PUT', 'DELETE').
        header_params (dict): Additional headers or parameters for the request.

    Returns:
        tuple: JSON response and status code.
    """
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
    """
    Retry an API call if the token has expired.

    Args:
        url (str): API endpoint URL.
        token (str): Authentication token.
        call_type (str): HTTP method ('GET', 'POST', 'PUT', 'DELETE').
        header_params (dict): Additional headers or parameters for the request.

    Returns:
        tuple: JSON response and status code.
    """
    response, status = call_with_token(url, token, call_type, header_params)
    if status == 401:
        print('Token expired, getting new token')
        token = get_token(AUTH_URL, YOUR_USERNAME, YOUR_PASSWORD)
        if token is None:
            print('Failed to get new token')
            return None, 401
        return call_and_retry(url, token, call_type, header_params)
    return response, status

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
    if timestamp is None:
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    alert_data = {
        "timestamp": timestamp,
        "machineID": machineID,
        "severity": severity,
        "description": description,
        "KPI": kpi,
        "aggr_type": aggr_type,
        "label": label
    }

    endpoint_url = f'{BASE_URL}/alert'
    response, status = call_and_retry(endpoint_url, auth_token, call_type='POST', header_params=alert_data)
    if status == 200:
        print(f'Alert successfully sent: {alert_data}')
    else:
        print(f'Failed to send alert: {alert_data} with status code {status}')

def request_raw_data(aggregationSelector, machines=None, dataTypes=None, start_time=None, end_time=None):
    """
    Request raw data from the server.

    Args:
        aggregationSelector (str): Aggregation type (e.g., 'sum', 'avg', 'max', 'min').
        machines (list, optional): List of machine IDs to filter data. Defaults to None.
        dataTypes (list, optional): List of data types to retrieve. Defaults to None.
        start_time (str, optional): Start time for data query. Defaults to None.
        end_time (str, optional): End time for data query. Defaults to None.

    Returns:
        dict: JSON response containing raw data.
    """
    required_data = {
        "machines": machines,
        "dataTypes": dataTypes,
        "aggregationSelector": aggregationSelector,
        "start_time": start_time,
        "end_time": end_time,
    }

    endpoint_url = f'{BASE_URL}/data/raw'
    response, status = call_and_retry(endpoint_url, auth_token, call_type='GET', header_params=required_data)
    if status == 200:
        print(f'Data successfully requested: {required_data}')
    else:
        print(f'Failed to get: {required_data} with status code {status}')
    return response

def parse_sensor_data(response, aggregationSelector):
    """
    Convert raw sensor data into a pandas DataFrame.

    Args:
        response (list): List of sensor data objects.
        aggregationSelector (str): Aggregation type applied to the data.

    Returns:
        pd.DataFrame: DataFrame containing parsed sensor data.
    """
    rows = []
    for sensor_data in response:
        machineID = sensor_data['machineID']
        kpi = sensor_data['kpi']
        timestamps = sensor_data['timestamp_series']
        values = sensor_data['value_series']
        for ts, val in zip(timestamps, values):
            rows.append({
                "time_stamp": ts,
                "machineID": machineID,
                "kpi": kpi,
                "aggr_type": aggregationSelector,
                "value": val,
            })
    return pd.DataFrame(rows)
