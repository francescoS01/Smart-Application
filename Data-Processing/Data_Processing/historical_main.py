"""
This file manages a historical data processing pipeline for machines that collect data on various Key Performance Indicators (KPIs) over time. 
The main processing stages include:

1. **Data Extraction**: Retrieves raw data from an API, applying different aggregation types (sum, average, min, max) and concatenating them into a single DataFrame.
2. **Preprocessing**: Applies preprocessing functions such as missing value imputation, trend drift analysis, and the creation of seasonal variables.
3. **Anomaly Detection**: Uses an anomaly detection algorithm on the historical data to identify outliers and flag anomalous values.
4. **Performance Prediction**: Performs future performance forecasting based on a time series regression model and appends prediction columns to the data.
5. **Data Saving**: Saves the processed data (including seasonalities and predictions) into a database for further use.

This pipeline is designed to be flexible and can be easily adapted for different types of machines and KPIs. Each step is modular, enabling independent testing and customization.
"""

# Import necessary libraries
import pandas as pd
import os
import pickle
import numpy as np
import pytz
from itertools import product 
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from Data_Processing.preprocessing_functions import *
from Data_Processing.anomalies_functions import *
from Data_Processing.prediction_functions import *
from Data_Processing.feature_store_utils import *
from Data_Processing.api_interaction import request_raw_data, parse_sensor_data


# Global configuration
REDIS_HOST = os.getenv("REDIS_HOSTNAME", "localhost")  # Redis host address (used for caching or data storage)
REDIS_PORT = os.getenv("REDIS_PORT", 6379)  # Redis port (default is 6379)
DB_HOSTNAME = os.getenv("DB_HOSTNAME", "localhost")  # Database host address (where the data will be stored)
REDIS_URL = f"{REDIS_HOST}:{REDIS_PORT}"  # Redis connection URL for communication with the Redis service

# Database and feature store initialization
tz = pytz.timezone("Europe/Rome")  # Set the timezone for the processing to European/Rome timezone
engine = new_engine(DB_HOSTNAME)  # Initialize the database engine (to interact with the DB)
store = start_store("./Feature_store")  # Initialize the feature store (store is used to hold features for machine learning models)

# Global constants for processing
card_imputation = 7  # Number of previous samples for imputing missing values (historical data used for imputation)
n_period = 4  # Number of periods used for trend drift analysis (trend drift analysis over this period)
n_future = 28  # Number of future values to predict (forecast horizon, in this case, 28 periods)
n_lags = 14  # Number of lagged values for the prediction model (to create lagged features for model)

# Function that processes the received data
def retrieve_data(start_time = None, end_time = None):
    """
    Function to retrieve raw data from an API for a given time range (start_time, end_time)
    and aggregate the data based on specified aggregation types (sum, avg, min, max).
    
    Args:
        start_time: Optional, the start time for data retrieval.
        end_time: Optional, the end time for data retrieval.
    
    Returns:
        A DataFrame containing the concatenated data for all aggregation types (sum, avg, min, max).
    """
    h_data = pd.DataFrame()  # Initialize an empty DataFrame to hold all the data
    aggr_type = ['sum', 'min', 'avg', 'max']  # List of aggregation types for API request
    
    for t in aggr_type:
        # Request raw data for each aggregation type from the API
        start_time_str = start_time.isoformat() if isinstance(start_time, datetime) else start_time
        end_time_str = end_time.isoformat() if isinstance(end_time, datetime) else end_time
        response = request_raw_data(aggregationSelector=t, start_time=start_time_str, end_time=end_time_str)
        #response = request_raw_data(aggregationSelector=t, start_time = start_time, end_time = end_time)
        # Parse the sensor data into a DataFrame for the specific aggregation type
        df_type = parse_sensor_data(response, t)
        # Concatenate the parsed data to the main DataFrame
        h_data = pd.concat([h_data, df_type], ignore_index=True)
    formatted_data = f"""
    Data Details:
    ---------------
    Timestamp  : from {h_data["timestamp"].min()} to {h_data["timestamp"].max()}
    Machine ID : {h_data["machineID"].unique()}
    KPI        : {h_data["kpi"].unique()}
    Aggr. Type : {h_data["aggr_type"].unique()}
    """
    print('Data successfully retreived!\n', formatted_data)
    return h_data  # Return the combined DataFrame with data from all aggregation types

# Historical main function for processing
def historical_processing(historical_data):
    """
    Main function for the historical part of the pipeline.
    Handles data preprocessing, anomaly detection, and performance prediction.
    
    Args:
        historical_data: DataFrame containing the historical data to be processed.
    
    Returns:
        None. The processed data is inserted into the database.
    """
    
    ### DATA: EXTRACTION FROM THE DATABASE
    # Extract conditions based on unique values from historical data for filtering
    conditions = {
        'machineID': historical_data['machineID'].unique().tolist(),
        'kpi': historical_data['kpi'].unique().tolist(),
        'aggregation_type': historical_data['aggr_type'].unique().tolist()
    }
    
    # Load exogenous threshold matrix from the feature store
    #ex_thr_matrix = get_data_from_sql("thresholds", engine, ['min_threshold', 'max_threshold'], conditions)
    # Mock up of thresholds' table
    names = historical_data['machineID'].unique()
    kpis = historical_data['kpi'].unique()
    cols = historical_data['aggr_type'].unique()
    combinations = list(product(names, kpis, cols))

    ex_thr_matrix = pd.DataFrame(combinations, columns=['machineID', 'kpi', 'aggr_type'])
    ex_thr_matrix['min_threshold'] = None
    ex_thr_matrix['max_threshold'] = None

    ####################################################

    ### PREPROCESSING
    # Call the preprocessing function that builds a dataframe with additional features such as residuals, trend drift, and imputation
    print('Everything ready for preprocessing')
    historical_data_analysis, seasonalities = preprocess_entire_h_data(historical_data, ex_thr_matrix)

    #################################################### 
    
    ### PROCESSING: ANOMALY DETECTION 
    # Call the anomaly detection function (this function trains models and appends an 'anomalies' column to the dataframe)
    print('Everything ready for anomaly detection')
    historical_data_analysis = detect_anomalies_from_dataframe(historical_data_analysis, contamination = 0.04, plot_flag = False, send_alert_flag = True)

    ####################################################
    
    ### PROCESSING: PERFORMANCE PREDICTION 
    # Call the performance prediction function to forecast future values ('n_future' days ahead) and add prediction columns
    print('Everything ready for performance prediction')
    historical_data_analysis = forecast_from_dataframe(historical_data_analysis, n_lags, n_future)

    ####################################################
    
    ### DATA: SAVE RESULTS IN THE DATABASE
    # Remove the 'residuals' column as it is not needed for saving
    historical_data_analysis.drop('residuals', axis=1, inplace=True)

    # renaming the columns for consistency with historical_store
    historical_data_analysis = historical_data_analysis.rename(columns={'machineID': 'machineid'})
    historical_data_analysis = historical_data_analysis.rename(columns={'aggr_type': 'aggregation_type'})
    historical_data_analysis['imputation'] = historical_data_analysis['imputation'].astype(bool)
    historical_data_analysis['anomaly'] = historical_data_analysis['anomaly'].astype(bool)

    seasonalities = seasonalities.rename(columns={'machineID': 'machineid'})
    seasonalities = seasonalities.rename(columns={'aggr_type': 'aggregation_type'})

    #save(streaming_data, iso_forest)  # saving the models inside the function
    output_dir = "saved_data_features"
    os.makedirs(output_dir, exist_ok = True)

    # Path to historical data file
    historical_file = os.path.join(output_dir, 'data_features.pkl')
    if os.path.exists(historical_file):
        with open(historical_file, 'rb') as f:
            existing_data = pickle.load(f)
        historical_data_analysis = pd.concat([existing_data, historical_data_analysis], ignore_index=True)
        historical_data_analysis.drop_duplicates(subset=['machineid', 'aggregation_type', 'timestamp'], inplace=True)
    with open(historical_file, 'wb') as f:
        pickle.dump(historical_data_analysis, f)
    print(f"Historical data saved to {historical_file}.")

   

    ####################################################
    ### INSERT DATA INTO THE DATABASE
    
    # Insert the processed data into the database under the 'historical_store' table
    try:
        #insert_data_to_sql(historical_data_analysis, 'historical_store', engine)
        insert_new_data(historical_data_analysis, 'historical_store', engine, store)
    except IntegrityError as e:
        # Check if the error is due to the unique key violation
        if "duplicate key value violates unique constraint" in str(e):
            print("The data already exists in the database, skipping insertion.")
        else:
            # If the error is not related to the unique key, re-raise the exception
            raise

    # Insert the seasonalities data into the database under the 'seasonalities' table
    try:
        insert_new_data(seasonalities, 'seasonalities', engine, store)
        #insert_data_to_sql(seasonalities, 'seasonalities', engine)
    except IntegrityError as e:
        # Check if the error is due to the unique key violation
        if "duplicate key value violates unique constraint" in str(e):
            print("The data already exists in the database, skipping insertion.")
        else:
            # If the error is not related to the unique key, re-raise the exception
            raise

