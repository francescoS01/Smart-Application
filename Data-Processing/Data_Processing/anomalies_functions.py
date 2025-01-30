# Processing: Anomaly Detection

"""
This script provides functions for anomaly detection in time series data using the Isolation Forest algorithm. 
The anomaly detection pipeline focuses on two primary use cases:

1. **Batch Processing**: Detecting anomalies from residuals obtained through seasonal decomposition of historical data.
2. **Streaming Data**: Identifying anomalies in real-time based on the prediction error from streaming data.

### Key Features:
- Utilizes the Isolation Forest algorithm, which is effective for detecting outliers in multidimensional data.
- Includes options to visualize detected anomalies for better interpretability.
- Supports integration with streaming pipelines for real-time anomaly detection.
- Sends alerts for detected anomalies, providing information about severity levels.

### Dependencies:
- pandas
- numpy
- matplotlib
- sklearn (IsolationForest)
- api_layer_alert (for sending alerts)

### Functions:
1. `detect_anomalies_from_decomposition`: Detects anomalies from residuals in batch data (historical data) based on seasonal decomposition.
2. `detect_anomalies_from_dataframe`: Iterates through a DataFrame and calls `detect_anomalies_from_decomposition` for each group of machine data based on conditions such as imputation rate.
3. `detect_anomalies_from_streaming_data`: Identifies anomalies in streaming data using a pre-trained Isolation Forest model.

### Usage:
- Import the necessary libraries and ensure dependencies are installed.
- Use `detect_anomalies_from_decomposition` for static datasets (historical data).
- Use `detect_anomalies_from_streaming_data` for real-time anomaly detection with streaming data.

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import pickle
import os
from tqdm import tqdm
from Data_Processing.api_interaction import send_alert 

def detect_anomalies_from_decomposition(streaming_data, residuals, contamination="auto", plot_flag=False, send_alert_flag = True):
    """
    Detect anomalies using residuals from seasonal decomposition.

    Parameters:
    - streaming_data: dict with machineID, kpi, aggr_type and value, useful for the send_alert function
    - residuals (pd.Series or list): The residuals from the seasonal decomposition.
    - contamination (str or float): Proportion of anomalies in the dataset for Isolation Forest. Default is "auto".
    - plot_flag (bool): If True, plots the anomalies on the residual series. Default is True.
    - send_alert_flag: flag for sending the alerts, True by default

    Returns:
    - anomaly_indices (pd.Index): Indices of the detected anomalies.
    - iso_forest (IsolationForest): Trained Isolation Forest model.
    """

    # Prepare residuals by removing NaN values
    residuals = pd.Series(residuals).dropna()

    # Create a DataFrame for the residuals
    residual_df = pd.DataFrame({'residuals': residuals})

    # Apply Isolation Forest for anomaly detection
    iso_forest = IsolationForest(contamination=contamination, random_state=1)  # Random state ensures reproducibility
    residual_df['anomaly'] = iso_forest.fit_predict(residual_df[['residuals']])
    residual_df['anomaly'] = residual_df['anomaly'].map({1: 0, -1: 1})  # Convert model output to binary format (0: normal, 1: anomaly)

    # Extract the indices of anomalies
    anomalies = residual_df[residual_df['anomaly'] == 1]['residuals']
    anomaly_indices = anomalies.index

    # to check 
    for idx in anomaly_indices:
        timestamp = streaming_data['timestamps'][idx]
        if send_alert_flag:
            # here severity is set to "medium" as these anomalies refer to historical data 
            send_alert(streaming_data["machineID"], "medium", "anomaly detected in historical data", streaming_data["kpi"], streaming_data["aggr_type"], 'Anomaly_detected', timestamp=timestamp)
        #############################################
    
    # Plot residuals with anomalies if plot_flag is True
    if plot_flag:
        plt.figure(figsize=(8, 4))
        plt.plot(residual_df.index, residual_df['residuals'], label='Residuals', color='blue')
        plt.scatter(
            anomaly_indices,
            residual_df.loc[anomaly_indices, 'residuals'],
            color='red', label='Anomalies', zorder=5
        )
        plt.title("Anomaly Detection Based on Residuals")
        plt.xlabel("Index")
        plt.ylabel("Residual Value")
        plt.legend()
        plt.show()

    #save(streaming_data, iso_forest)  # saving the models inside the function
    output_dir = "saved_iso_model"
    os.makedirs(output_dir, exist_ok = True)
    filename = os.path.join(output_dir, f'iso_model_{streaming_data["machineID"]}_{streaming_data["kpi"]}_{streaming_data["aggr_type"]}.pkl')
    with open(filename, 'wb') as f:
        pickle.dump(iso_forest, f) 
    
    return anomaly_indices, iso_forest


def detect_anomalies_from_dataframe(df, contamination="auto", plot_flag=False, send_alert_flag=True):
    """
    Iterate through the DataFrame and call detect_anomalies_from_decomposition 
    for each combination of machineID, kpi, and aggr_type where most of 
    the 'imputation' values are non-null. Anomalies are saved as a new column.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing the data. Must include 'timestamp', 'residuals', and 'imputation'.
    - contamination (str or float): Proportion of anomalies in the dataset for Isolation Forest. Default is "auto".
    - plot_flag (bool): If True, plots the anomalies on the residual series. Default is False.
    - send_alert_flag (bool): If True, sends alerts for detected anomalies. Default is True.
    
    Returns:
    - pd.DataFrame: The input DataFrame with an additional 'anomaly' column.
    """
    # Group by 'machineID', 'kpi', and 'aggr_type'
    grouped = df.groupby(['machineID', 'kpi', 'aggr_type'])

    # Create a copy of the DataFrame to store anomalies
    df['anomaly'] = 0  # Default value: no anomalies

    for (machineID, kpi, aggr_type), group in tqdm(grouped):
        # Check if the average of 'imputation' is less than 0.15
        imputation_mean = group['imputation'].mean()

        if imputation_mean < 0.15:  # If the majority of values are not imputated

            residuals = group['residuals'].values  # Extract residuals for the current group
            timestamps = group['timestamp'].values  # Extract the timestamp column

            streaming_data = {
                'machineID': machineID,
                'kpi': kpi,
                'aggr_type': aggr_type,
                'timestamps': timestamps
            }

            # Call the detect_anomalies_from_decomposition function
            anomaly_indices, iso_forest = detect_anomalies_from_decomposition(
                streaming_data,
                residuals,
                contamination=contamination,
                plot_flag=plot_flag,
                send_alert_flag=send_alert_flag
            )

            # Convert anomaly_mask to a list if needed
            anomaly_mask = pd.Series(0, index=range(len(residuals)))
            anomaly_mask.loc[anomaly_indices] = 1
            anomaly_mask = anomaly_mask.tolist()

            # Update historical_data_analysis
            for i, timestamp in enumerate(timestamps):
                df.loc[
                    (df['machineID'] == machineID) &
                    (df['kpi'] == kpi) &
                    (df['aggr_type'] == aggr_type) &
                    (df['timestamp'] == timestamp),
                    'anomaly'
                ] = anomaly_mask[i]

    return df


            

def detect_anomalies_from_streaming_data(streaming_data, prediction_error, iso_forest, send_alert_flag = True):
    """
    Detects anomalies in streaming data using a pre-trained Isolation Forest model.

    Parameters:
    - streaming_data: dict with machineID, kpi, aggr_type and value, useful for the send_alert function
    - prediction_error (float): The difference between the actual and predicted values (residual).
    - iso_forest (IsolationForest): A pre-trained Isolation Forest model.
    - send_alert_flag: flag for sending the alerts, True by default

    Returns:
    - anomaly (int): 1 if the current data point is an anomaly, 0 if it is normal.
    """

    # Convert the prediction error into a DataFrame for compatibility with the Isolation Forest model
    prediction_error_df = pd.DataFrame([prediction_error], columns=['residuals'])

    # Use the pre-trained Isolation Forest model to predict anomalies
    anomaly_bool = iso_forest.predict(prediction_error_df)
    scores = iso_forest.decision_function(prediction_error_df)

    # Map the model output to binary format (0: normal, 1: anomaly)
    anomaly_bool = pd.Series(anomaly_bool).map({1: 0, -1: 1})

    # If an anomaly is detected, trigger a warning function (replace with actual implementation)
    if anomaly_bool[0] == 1:
        if send_alert_flag and scores < -0.5: # high severity 
            send_alert(streaming_data["machineID"], "high", "An important anomaly has been detected in the streaming data", streaming_data["kpi"], streaming_data["aggr_type"], 'Anomaly_detected', timestamp=None)
        elif send_alert_flag and scores > -0.5: # medium severity 
            send_alert(streaming_data["machineID"], "medium", "A minor anomaly has been detected in the streaming data", streaming_data["kpi"], streaming_data["aggr_type"], 'Anomaly_detected', timestamp=None)
    # Return the anomaly status (1 for anomaly, 0 for normal)
    return anomaly_bool[0]
