"""
This script processes streaming data for machine KPIs (Key Performance Indicators). It performs data extraction, 
preprocessing, anomaly detection, trend drift analysis, and future performance prediction. The results are saved 
back to the database for further analysis. The main function `streaming_processing` is designed to handle real-time 
data and interface with pre-trained models and databases.
"""

# Required libraries
import os  # For environment variables and file path operations
import pickle  # To load and save machine learning models
import numpy as np  # For numerical computations
import pandas as pd  # For handling tabular data
import pytz  # For timezone management
from datetime import datetime, timedelta  # For working with timestamps
from preprocessing_functions import *  # Preprocessing utilities (user-defined)
from anomalies_functions import *  # Anomaly detection utilities (user-defined)
from prediction_functions import *  # Prediction utilities (user-defined)
from feature_store_utils import *  # Feature store interaction utilities (user-defined)
import matplotlib.pyplot as plt  # For plotting (if necessary)

# Global configuration
REDIS_HOST = os.getenv("REDIS_HOSTNAME", "localhost")  # Redis host address
REDIS_PORT = os.getenv("REDIS_PORT", 6379)  # Redis port
DB_HOSTNAME = os.getenv("DB_HOSTNAME", "localhost")  # Database host address
REDIS_URL = f"{REDIS_HOST}:{REDIS_PORT}"  # Redis connection URL

# Database and feature store initialization
tz = pytz.timezone("Europe/Rome")  # Set timezone
engine = new_engine(DB_HOSTNAME)  # Database engine initialization
store = start_store(".")  # Feature store initialization

# Global constants for processing
card_imputation = 7  # Number of previous samples for imputing missing values
n_period = 4  # Number of periods used for trend drift analysis
n_future = 28  # Number of future values to predict
n_lags = 14  # Number of lagged values for the prediction model
iso_min_samples = 100  # Minimum samples to train the isolation forest
ffnn_min_samples = 100  # Minimum samples to train the FFNN

def streaming_processing(streaming_data):
    """
    Processes streaming data for a machine's KPI, performing the following tasks:
    1. Extracts data from a database (based on machineID, KPI, and aggregation type).
    2. Preprocesses data by imputing missing values and detecting trend drift.
    3. Detects anomalies using an isolation forest model.
    4. Optionally detects performance degradation.
    5. Predicts future values using a pre-trained FFNN model.
    6. Saves processed results (e.g., imputed values, anomalies, trend drift, predictions) back to the database.

    Parameters:
        streaming_data (dict): A dictionary with the following keys:
            - "machineID": Identifier for the machine
            - "kpi": The KPI to process
            - "aggr_type": Aggregation type for the KPI
            - "value": Current KPI value
            - "time_stamp": Timestamp of the data point

    Returns:
        None
    """
    
    # --- Data extraction ---
    # Extract value and conditions from the streaming data
    value = streaming_data["value"]
    conditions = {
        'machineID': streaming_data['machineID'],
        'kpi': streaming_data['kpi'],
        'aggregation_type': streaming_data['aggr_type']
    }

    # Retrieve selected features and thresholds from the feature store
    selected_f_df = get_filtered_online_features(store, "seasonalities", ['selected_f'], conditions)
    selected_f = selected_f_df.iloc[0]["selected_f"]
    thresholds_df = get_filtered_online_features(store, "thresholds", ['min_threshold', 'max_threshold'], conditions)
    ex_lower_thr = thresholds_df.iloc[0]["min_threshold"]
    ex_higher_thr = thresholds_df.iloc[0]["max_threshold"]

    # Retrieve future predictions from the feature store
    next_days_predictions_df = get_filtered_online_features(store, "historical_store", ['next_days_predictions'], conditions)
    next_days_predictions = next_days_predictions_df.iloc[0]["next_days_predictions"]
    predicted_value = next_days_predictions[0]

    # Define the window size for historical data retrieval
    window_size = max(card_imputation, selected_f * (n_period + 1) - 1, n_lags - 1)
    current_timestamp = pd.Timestamp(streaming_data["time_stamp"])
    start_time = current_timestamp - timedelta(days=window_size)
    end_time = current_timestamp - timedelta(days=1)

    # Retrieve historical data from the database
    TimeSeriesAndImputationMask_df = get_data_from_sql("historical_store", engine, ['value', 'imputation'], conditions, start_time, end_time)
    time_series = TimeSeriesAndImputationMask_df["value"]
    imputation_mask = TimeSeriesAndImputationMask_df["imputation"]

    # --- Preprocessing ---
    # Apply preprocessing functions to clean and process the data
    _, trend_drift, imp_value, imputation_bool = preprocess_s_data(
        streaming_data, value, time_series, imputation_mask, ex_lower_thr, ex_higher_thr, selected_f)

    # Initialize variables for further processing
    anomaly = None
    next_predicted_values = pd.Series([None] * n_future)
    confidence_interval_lower = pd.Series([None] * n_future)
    confidence_interval_upper = pd.Series([None] * n_future)

    def is_nan(value):
        """Helper function to check if a value is NaN."""
        if isinstance(value, (float, int)):
            return np.isnan(value)
        elif isinstance(value, np.ndarray):
            return np.isnan(value).all()
        return pd.isna(value)

    if not is_nan(imp_value):
        # --- Trend Drift Analysis ---
        if trend_drift != 0:
            # Retrain seasonality model if a trend drift is detected
            window_size_iso = max(4 * selected_f, iso_min_samples)
            iso_start_time = current_timestamp - timedelta(days=window_size_iso)
            TimeSeries_df = get_data_from_sql("historical_store", engine, ['value'], conditions, iso_start_time, end_time)
            time_series_iso_retraining = TimeSeries_df["value"]
            best_decomposition, new_selected_f = analysis_seasonality(time_series_iso_retraining)
            _, _ = detect_anomalies_from_decompostion(
                streaming_data, best_decomposition.resid, contamination=0.04, send_alert_flag=False)

            # Store updated seasonality parameters in the database
            seas_data = {
                'timestamp': current_timestamp,
                'machineID': streaming_data['machineID'],
                'kpi': streaming_data['kpi'],
                'aggregation_type': streaming_data['aggr_type'],
                'selected_f': new_selected_f,
            }
            seas_df = pd.DataFrame(seas_data)
            insert_new_data(seas_df, 'seasonalities', engine, store)

        # --- Anomaly Detection ---
        filename = os.path.join("saved_iso_model", f'iso_model_{streaming_data["machineID"]}_{streaming_data["kpi"]}_{streaming_data["aggr_type"]}.pkl')
        with open(filename, 'rb') as f:
            iso_forest = pickle.load(f)
        prediction_error = imp_value - predicted_value
        anomaly = detect_anomalies_from_streaming_data(
            streaming_data, prediction_error, iso_forest, send_alert_flag=True)

        # --- Performance Prediction ---
        filename = os.path.join("saved_ffnn_model", f'ffnn_model_{streaming_data["machineID"]}_{streaming_data["kpi"]}_{streaming_data["aggr_type"]}.pkl')
        with open(filename, 'rb') as f:
            ffnn_dict = pickle.load(f)
        trained_ffnn = ffnn_dict["model"]
        scaler = ffnn_dict["model"]
        std_residuals = ffnn_dict["std_residuals"]
        next_predicted_values, confidence_interval_lower, confidence_interval_upper = forecast_future(
            pd.concat([time_series, pd.Series(imp_value)]), trained_ffnn, scaler, std_residuals, n_future, n_lags, plot_results=False)

        # --- Save Results in the Database ---
        h_store_data = {
            'timestamp': current_timestamp,
            'machineID': streaming_data['machineID'],
            'kpi': streaming_data['kpi'],
            'aggregation_type': streaming_data['aggr_type'],
            'value': imp_value,
            'imputation': imputation_bool,
            'anomaly': anomaly,
            'trend_drift': trend_drift,
            'next_days_predictions': next_predicted_values,
            'confidence_interval_lower': confidence_interval_lower,
            'confidence_interval_upper': confidence_interval_upper,
        }
        h_store_df = pd.DataFrame(h_store_data)
        insert_new_data(h_store_df, 'historical_store', engine, store)
