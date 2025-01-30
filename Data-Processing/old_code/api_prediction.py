# Import necessary libraries
import requests
import os
import time  # For the listening loop
import pandas as pd  # To handle time series data
import numpy as np  # For data preparation
import pickle  # For loading your trained model
from prediction_functions import forecast_future, forecast_with_ffnn  # Import model-related functions

# API configuration
HOSTNAME = os.getenv('API_HOSTNAME', 'localhost')
PORT = 443
BASE_URL = f'https://{HOSTNAME}:{PORT}'

YOUR_USERNAME = 'sysadmin'  # Replace with real credentials
YOUR_PASSWORD = 'sysadmin'

AUTH_URL = f'{BASE_URL}/user/login'
PREDICTION_ENDPOINT = f'{BASE_URL}/prediction/request'
RESULTS_ENDPOINT = f'{BASE_URL}/prediction/response'

# Authentication token
auth_token = None


# Function to get an authentication token
def get_token(url, username, password):
    headers = {'username': username, 'password': password}
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


# Function to call API endpoints with the token
def call_with_token(url, token, call_type='GET', header_params=None, data=None):
    headers = {} if header_params is None else header_params
    headers['Authorization'] = token
    if call_type == 'GET':
        response = requests.get(url, headers=headers, verify=False)
    elif call_type == 'POST':
        response = requests.post(url, headers=headers, json=data, verify=False)
    elif call_type == 'PUT':
        response = requests.put(url, headers=headers, verify=False)
    elif call_type == 'DELETE':
        response = requests.delete(url, headers=headers, verify=False)
    else:
        print('Unknown call type')
        return None, None
    if response.status_code == 500:
        print('Server error:', response.reason)
        return None, response.status_code
    elif response.status_code == 400:
        print('Bad request:', response.reason)
        return None, response.status_code
    elif response.status_code == 401:
        print('Unauthorized')
        return None, response.status_code
    elif response.status_code == 200:
        return response.json(), response.status_code
    else:
        print('Unknown error:', response.reason)
        return None, response.status_code


# Function to retry API calls if the token has expired
def call_and_retry(url, token, call_type='GET', header_params=None, data=None):
    response, status = call_with_token(url, token, call_type, header_params, data)
    if status == 401:
        print('Token expired, getting new token')
        token = get_token(AUTH_URL, YOUR_USERNAME, YOUR_PASSWORD)
        if token is None:
            print('Failed to get new token')
            return None, 401
        return call_and_retry(url, token, call_type, header_params, data)
    return response, status


# Function to load the trained model and scaler from pickle files
def load_model_and_scaler(machine, kpi_name, aggr_type):
    """
    Load the trained FFNN model and its associated scaler from pickle files.

    Parameters:
    - machine (str): Machine name.
    - kpi_name (str): KPI name.
    - aggr_type (str): Aggregation type.

    Returns:
    - model: The trained FFNN model.
    - scaler: The scaler object used during training.
    """
    model_path = f"models/{machine}_{kpi_name}_{aggr_type}_model.pkl"
    scaler_path = f"models/{machine}_{kpi_name}_{aggr_type}_scaler.pkl"

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Model or scaler not found for {machine}, {kpi_name}, {aggr_type}")

    with open(model_path, "rb") as model_file, open(scaler_path, "rb") as scaler_file:
        model = pickle.load(model_file)
        scaler = pickle.load(scaler_file)

    return model, scaler

# Function to generate predictions using the FFNN model
def make_prediction(data):
    """
    Use the FFNN model to predict future values based on machine ID, KPI, aggregation type, 
    and the number of steps in the future.

    Parameters:
    - data (dict): The prediction request data containing machineID, kpi_name, aggr_type, and n_future.

    Returns:
    - dict: The prediction results including future values or an error message.
    """
    try:
        print("Preparing prediction data...")

        # Extract required information
        machineID = data["machineID"]
        kpi_name = data["kpi_name"]
        aggr_type = data["aggr_type"]
        n_future = data.get("n_future", 21)  # Default to 21 steps if not provided

        # Load the model and scaler
        model, scaler = load_model_and_scaler(machineID, kpi_name, aggr_type)

        # Prepare the time series data from the request
        # Here dal topic 2
        time_series = pd.Series(data["time_series"], index=pd.to_datetime(data["dates"]))

        # Generate future predictions
        predictions = forecast_future(
            time_series=time_series,
            trained_ffnn=model,
            scaler=scaler,
            n_future=n_future,
            n_lags=14,  # fixed lag for simplicity
            plot_results=False
        )

        # Return the predictions in a dictionary
        return {
            "machineID": machineID,
            "kpi_name": kpi_name,
            "aggr_type": aggr_type,
            "predictions": predictions.tolist(),
            "n_future": n_future
        }

    except Exception as e:
        print(f"Error during prediction: {e}")
        return {"error": str(e)}


# Main listener loop
def listen_for_requests():
    global auth_token
    auth_token = get_token(AUTH_URL, YOUR_USERNAME, YOUR_PASSWORD)

    if auth_token is None:
        print("Failed to authenticate. Exiting.")
        return

    while True:
        print("Listening for requests...")

        # Fetch new prediction requests
        prediction_request, status = call_and_retry(PREDICTION_ENDPOINT, auth_token)
        if status == 200 and prediction_request:
            print("Received prediction request:", prediction_request)

            # Generate predictions
            prediction = make_prediction(prediction_request)

            # Send the results back to the API
            response, response_status = call_and_retry(
                RESULTS_ENDPOINT, auth_token, call_type="POST", data=prediction
            )

            if response_status == 200:
                print("Prediction sent successfully:", response)
            else:
                print("Failed to send prediction:", response_status)
        else:
            print("No requests or error:", status)

        # Wait a few seconds before checking again
        time.sleep(5)


# Start the listener
if __name__ == "__main__":
    listen_for_requests()

