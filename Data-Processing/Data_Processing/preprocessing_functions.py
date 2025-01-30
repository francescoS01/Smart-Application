"""
Historical and Streaming Data Preprocessing

This preprocessing module manages the data flow for both historical and streaming KPI data collected from machines. The main operations include handling missing values, analyzing seasonality, detecting data inconsistencies, and managing trend drift. Below are the key steps implemented:

1. **Historical Data Preprocessing (`preprocess_h_data`)**:
   - **Handling Missing Values**: A function is used to handle missing values by creating an imputation mask indicating the values that were imputed in the time series.
   - **Seasonality Analysis**: The seasonality of the KPI data is analyzed to determine the most appropriate seasonal frequency for the historical time series, improving trend prediction.
   - **Inconsistency Detection**: Inconsistencies in the data are identified by comparing values to exogenous thresholds (minimum and maximum) to detect anomalies.
   - **Trend Drift Detection**: Trend drift is analyzed recursively by comparing the trend of each point in the time series to previous ones. This allows monitoring the stability of trends over time.

2. **Preprocessing Entire Historical Dataset (`preprocess_entire_h_data`)**:
   - This function handles the entire historical dataset, performing data consistency validation, seasonality analysis, inconsistency detection, and trend drift monitoring for all combinations of `machineID`, `kpi`, and `aggr_type`.
   - It returns a DataFrame with the analysis results, including residuals from decomposition, trend drift, values, and imputation information.

3. **Streaming Data Preprocessing (`preprocess_s_data`)**:
   - Manages individual streaming data points by applying imputation for missing values, detecting inconsistencies (such as anomalies or spikes), and monitoring trend drift.
   - If the current value is valid, inconsistency detection and trend drift analysis are performed, and the time series is updated with the corrected data.

These functions support accurate and real-time analysis of data, enabling performance monitoring and detection of anomalies or trend changes for both historical and streaming data.
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp
from statsmodels.tsa.seasonal import seasonal_decompose 
from datetime import datetime
from itertools import product
from tqdm import tqdm
from Data_Processing.api_interaction import send_alert 

def check_invalid_data(data):
    """
    Checks and updates KPI data for inconsistencies. This function performs several checks on the data:
    1. Cycle consistency: Ensures the sum of good and bad cycles equals the total cycles.
    2. Energy consumption consistency: Verifies that total consumption is the sum of idle and working consumption.
    3. Cost consistency: Validates that total cost equals the sum of idle and working costs.
    If any inconsistency is found, the relevant data is set to NaN and a warning is sent.

    Parameters:
    - data: DataFrame containing KPI data with columns ['timestamp', 'machineID', 'kpi', 'aggr_type', 'value'].
    """
    for machineID in tqdm(data['machineID'].unique()):
        for timestamp in data['timestamp'].unique():

            # Check cycle consistency
            try:
                good_cycles = data[(data['timestamp'] == timestamp) & (data['machineID'] == machineID) & (data['kpi'] == 'good_cycles') & (data['aggr_type'] == 'sum')]['value'].values[0]
                cycles = data[(data['timestamp'] == timestamp) & (data['machineID'] == machineID) & (data['kpi'] == 'cycles') & (data['aggr_type'] == 'sum')]['value'].values[0]
                bad_cycles = data[(data['timestamp'] == timestamp) & (data['machineID'] == machineID) & (data['kpi'] == 'bad_cycles') & (data['aggr_type'] == 'sum')]['value'].values[0]
                if cycles != good_cycles + bad_cycles:
                    # fixed severity "low"
                    send_alert(machineID, "low", f'Inconsistency for {machineID} at {timestamp}: cycle rule not respected.', 'cycles', 'sum', 'Invalid data', timestamp=None)
                    data.loc[(data['timestamp'] == timestamp) & (data['machineID'] == machineID) & (data['kpi'].isin(['good_cycles', 'bad_cycles', 'cycles'])) & (data['aggr_type'] == 'sum'), 'value'] = np.NaN
            except IndexError:
                print(f'Missing data for {machineID} at {timestamp} (cycle rule)')

            # Check energy consumption consistency
            try:
                consumption_working = data[(data['timestamp'] == timestamp) & (data['machineID'] == machineID) & (data['kpi'] == 'consumption_working') & (data['aggr_type'] == 'sum')]['value'].values[0]
                consumption = data[(data['timestamp'] == timestamp) & (data['machineID'] == machineID) & (data['kpi'] == 'consumption') & (data['aggr_type'] == 'sum')]['value'].values[0]
                consumption_idle = data[(data['timestamp'] == timestamp) & (data['machineID'] == machineID) & (data['kpi'] == 'consumption_idle') & (data['aggr_type'] == 'sum')]['value'].values[0]
                if consumption != consumption_idle + consumption_working:
                    # fixed severity "low"
                    send_alert(machineID, "low", f'Inconsistency for {machineID} at {timestamp}: consumption rule not respected.', 'consumption', 'sum', 'Invalid data', timestamp=None)
                    data.loc[(data['timestamp'] == timestamp) & (data['machineID'] == machineID) & (data['kpi'].isin(['consumption_working', 'consumption_idle', 'consumption'])) & (data['aggr_type'] == 'sum'), 'value'] = np.NaN
            except IndexError:
                print(f'Missing data for {machineID} at {timestamp} (consumption rule)')

            # Check cost consistency
            try:
                cost_working = data[(data['timestamp'] == timestamp) & (data['machineID'] == machineID) & (data['kpi'] == 'cost_working') & (data['aggr_type'] == 'sum')]['value'].values[0]
                cost = data[(data['timestamp'] == timestamp) & (data['machineID'] == machineID) & (data['kpi'] == 'cost') & (data['aggr_type'] == 'sum')]['value'].values[0]
                cost_idle = data[(data['timestamp'] == timestamp) & (data['machineID'] == machineID) & (data['kpi'] == 'cost_idle') & (data['aggr_type'] == 'sum')]['value'].values[0]
                if cost != cost_idle + cost_working:
                    # fixed severity "low"
                    send_alert(machineID, "low", f'Inconsistency for {machineID} at {timestamp}: cost rule not respected.', 'cost', 'sum', 'Invalid data', timestamp=None)
                    data.loc[(data['timestamp'] == timestamp) & (data['machineID'] == machineID) & (data['kpi'].isin(['cost_working', 'cost_idle', 'cost'])) & (data['aggr_type'] == 'sum'), 'value'] = np.NaN
            except IndexError:
                print(f'Missing data for {machineID} at {timestamp} (cost rule)')

            # Additional inconsistency checks can be added here if needed
            # try:
              # inconsistency rule
            # except

    return None



def handle_missing_values(streaming_data, value, time_series, imputation_mask, card_imputation=7, send_alert_flag = True):
    """
    Handle missing values in a Pandas Series. If the missing ratio exceeds 30%, 
    replaces the value with "Nan". Otherwise, fills missing values with the 
    mean of the previous 'card_imputation' valid values.

    Parameters:
    - streaming_data: dict with machineID, kpi, aggr_type and value 
    - value: The value to be processed (scalar or Pandas Series) 
    - time_series: Pandas Series with the KPI time series data.
    - imputation_mask: Mask indicating the positions of missing values.
    - card_imputation: Number of previous values used for imputation (default is 7).
    - send_alert_flag: function for sending alerts to API layer, True by default

    Returns:
    - imputation_bool: Boolean indicating if the value was imputed (1 if imputed, 0 if not).
    - imp_value: The imputed value (or original value if no imputation was necessary).
    """

    # Convert 'value' to a NumPy array if it is a Pandas Series
    if isinstance(value, pd.Series):
        value = value.to_numpy()

    # Convert 'value' to a NumPy array if it is a scalar
    if np.isscalar(value):
        value = np.array([value])

    # If the data is present (not NaN), no imputation is needed
    if not np.isnan(value)[0]:  
        imputation_bool = 0
        imp_value = value
    else:  # The data is missing (NaN)
        imputation_bool = 1
        if len(time_series) >= card_imputation:  # Check if we have enough previous data for imputation
            # Calculate the missing data ratio from the last 'card_imputation' entries
            missing_ratio = imputation_mask[-card_imputation:].mean()
            if missing_ratio > 0.9:
                imp_value = np.nan
            # If the missing ratio is too high, set the value as NaN and trigger a warning
            elif missing_ratio > 0.5:
                imp_value = np.nan
                if send_alert_flag:
                    send_alert(streaming_data["machineID"], "high", f'Anomalous increase in missing data, more than 50% missing data for the last {card_imputation} samples', streaming_data["kpi"], streaming_data["aggr_type"], 'missing_data', timestamp=streaming_data['current_timestamps'])
            elif missing_ratio > 0.3:
                imp_value = np.nan
                if send_alert_flag:
                    send_alert(streaming_data["machineID"], "medium", f'Anomalous increase in missing data, 30% to 50% missing data for the last {card_imputation} samples', streaming_data["kpi"], streaming_data["aggr_type"], 'missing_data', timestamp=streaming_data['current_timestamps'])
            else:
                # Impute the missing value with the mean of the previous 'card_imputation' valid values
                mean_value = time_series.tail(card_imputation).mean()
                imp_value = mean_value
        else:
            # If there is not enough data to calculate the mean, return NaN and print a message
            #print('Not enough data to calculate the mean for the missing value.')
            imp_value = np.nan
    return imputation_bool, imp_value


def handle_missing_values_h(streaming_data, time_series, send_alert_flag = True):
    """
    Iterates over a time series and handles missing values by calling 
    the 'handle_missing_values' function for each value. The function 
    replaces missing values based on the imputation method and keeps track 
    of the imputation process with an imputation mask.

    Parameters:
    - time_series: Pandas Series containing the KPI time series data with potential missing values.
    - streaming_data: dict with machineID, kpi, aggr_type and value 
    - send_alert_flag: function for sending alerts to API layer, True by default

    Returns:
    - time_series: Updated time series with missing values handled.
    - imputation_mask: Mask indicating whether a value was imputed (1 if imputed, 0 if not).
    """

    # Initialize an array to keep track of imputed values (0 means not imputed, 1 means imputed)
    imputation_mask = np.zeros(len(time_series))

    # Iterate over each value in the time series
    for i in range(len(time_series)):
        timestamp = streaming_data["current_timestamps"].iloc[i]
        current_streaming_data = streaming_data.copy()
        current_streaming_data['current_timestamps'] = timestamp
        # Call handle_missing_values to process the current value and its imputation
        imputation_bool, imp_value = handle_missing_values(current_streaming_data, time_series.iloc[i], time_series.iloc[:i], imputation_mask[:i], send_alert_flag = send_alert_flag)
        
        # Save the imputation status (1 for imputed, 0 for not)
        imputation_mask[i] = imputation_bool
        
        # Update the time series with the imputed value
        time_series.iloc[i] = imp_value

    return time_series, imputation_mask


def analysis_seasonality(time_series, freq = [7, 30], plot_flag = False):
    """
    Analyzes the seasonality of a time series for a specific machine and KPI.

    Parameters:
    - time_series: Pandas Series with the KPI time series data.
    - freq: List of seasonality frequencies (e.g., 7 for weekly, 30 for monthly) to analyze.
    - plot_flag: Flag to decide whether to plot the seasonal decomposition results.

    Returns:
    - best_decomposition: Best seasonal decomposition object based on the analysis.
    - selected_f: The selected frequency that provides the best seasonal contribution.
    """

    # Convert the time series to a numpy array for processing
    time_series = time_series.values

    # Compute the total variance of the series (used for assessing seasonal contribution)
    total_variance = np.var(time_series)

    # Initialize variables for tracking the best seasonality decomposition and frequency
    best_seas_contribuition = 0
    best_decomposition = None
    selected_f = None

    # Loop through the given frequencies to analyze the seasonality for each one
    for f in freq:
        # Check if there is enough data to analyze the seasonality at the current frequency
        if len(time_series) < f:
            print(f"Not enough data to analyze seasonality (at least {f} points are required).")
        else:
            # Perform the seasonal decomposition of the time series
            decomposition = seasonal_decompose(time_series, model='additive', period=f)

            # Compute the seasonal contribution (the proportion of variance explained by seasonality)
            if total_variance == 0:
                seas_contribuition = 0
            else:
                seas_contribuition = np.var(decomposition.seasonal) / total_variance

            # Update the best seasonality if the current one explains more variance
            if seas_contribuition >= best_seas_contribuition:
                selected_f = f
                best_decomposition = decomposition
                best_seas_contribuition = seas_contribuition

            # Comment: a threshold should be used to check whether a significant percentage of the total variance of the time_series is actually explained 
            # by the variance of the seasonality (seas_contribution) that therefore allows us to compute the trend drift considering a seasonality in the 
            # time_series. This threshold is not implemented yet, but is an additional feature that should be taken into account. 
            # possible solution: if seas_contribution < threshold:
                                    # the trend drift is detected by applying KS on the trend that comes from the decomposition! 
            # this implies changing some functions, but could be done in the future. 

    # Plot the seasonal decomposition if plot_flag is True
    if plot_flag == True:
        best_decomposition.plot()
        plt.suptitle(f'Additive Model - Seasonality for {selected_f}', fontsize=12, y=1.02)
        plt.show()

    # Return the best decomposition and the selected frequency
    return best_decomposition, selected_f

# N.B.
# Multiplicative Model cannot be implemented if there are zeros in the data.
# One can possibly add a bias to the series, apply a log transformation or eventually filter out zero data but this can
# induce possible misinterpretations--> Hockam's razor

def perform_stat_analysis(time_series):
    """
    Perform statistical analysis to compute quartiles for a single time series.

    Parameters:
    - time_series: Time series of data for a specific machine, KPI, and column.

    Returns:
    - A dictionary containing statistical parameters such as quartiles, mean, and standard deviation.
    """

    # Check if the time series is empty
    if time_series.empty:
        print(f"No data available for the time series.")
    else:
        # Compute quartiles: Q1, Q2 (median), Q3, and Q4 (maximum value)
        q1 = time_series.quantile(0.25)  # 1st quartile (25th percentile)
        q2 = time_series.quantile(0.50)  # 2nd quartile (median, 50th percentile)
        q3 = time_series.quantile(0.75)  # 3rd quartile (75th percentile)
        q4 = time_series.max()           # Max value (end of the 4th quartile)

        # Construct the result dictionary with key statistics
        data_parameters = {
            "min": time_series.min(),     # Minimum value
            "Q1": q1,                     # 1st quartile
            "Q2": q2,                     # Median (2nd quartile)
            "Q3": q3,                     # 3rd quartile
            "Q4": q4,                     # Maximum value (4th quartile)
            "Mean": time_series.mean(),   # Mean value
            "Std": time_series.std()      # Standard deviation
        }

        # Print out the computed data parameters
        print(f"Data parameters for the time series are: {data_parameters}")

    # Return the dictionary containing the statistical parameters
    return data_parameters


def detect_inconsistencies_exogenous(streaming_data, time_series, exogenous_lower_thr=None, exogenous_higher_thr=None, send_alert_flag = True):
    """
    Detect inconsistencies in a time series based on exogenous thresholds.

    Parameters:
    - streaming_data: dict with machineID, kpi, aggr_type and value
    - time_series: Pandas Series with the KPI time series data.
    - exogenous_lower_thr: Lower threshold for detection (optional). If provided, values below this threshold are flagged.
    - exogenous_higher_thr: Higher threshold for detection (optional). If provided, values above this threshold are flagged.
    - send_alert_flag: function for sending alerts to API layer, True by default
    - current_timestamps: Pandas Series or list of timestamps corresponding to the time series.


    Returns:
    - inconsistencies_flag: A NumPy array with flags indicating whether inconsistencies are detected (1 if inconsistent, 0 otherwise).
    """
    # Initialize the inconsistencies flag array with zeros
    inconsistencies_flag = np.zeros(len(time_series))

    # Loop through the time series to check for inconsistencies
    for i in range(len(time_series)):
        # Check if the current value is outside the provided thresholds
        # If an inconsistency is found, set the corresponding flag to 1 and send a warning

        # Get the current timestamp
        if isinstance(streaming_data["current_timestamps"], str):
            timestamp = streaming_data["current_timestamps"]
        else:
            timestamp = streaming_data["current_timestamps"].iloc[i]

        if exogenous_lower_thr is not None and time_series.iloc[i] < exogenous_lower_thr:
            inconsistencies_flag[i] = 1
            if send_alert_flag:
                send_alert(streaming_data["machineID"], "low", f'Found inconsistency at index {i}: the value is lower than the min threshold', streaming_data["kpi"], streaming_data["aggr_type"], 'Exogenous_inconsistency', timestamp=timestamp)
            # severity is evaluated as low since inconsistency wrt the exogenous threshold is interpreted as a numerical error, due to chance 
        elif exogenous_higher_thr is not None and time_series.iloc[i] > exogenous_higher_thr:
            inconsistencies_flag[i] = 1
            if send_alert_flag:
                send_alert(streaming_data["machineID"], "low", f'Found inconsistency at index {i}: the value is higher than the max threshold', streaming_data["kpi"], streaming_data["aggr_type"], 'Exogenous_inconsistency', timestamp=timestamp)
            
    # Return the array of inconsistency flags
    return inconsistencies_flag


def detect_trend_drift_recursive(streaming_data, time_series, selected_f, n_period = 4, send_alert_flag = True):
    """
    Detects trend drift by comparing the current distribution with the seasonality pattern.
    Uses statistical tests (Kolmogorov-Smirnov test) to evaluate changes in the data.

    Parameters:
    - streaming_data: dict with machineID, kpi, aggr_type and value
    - time_series: Pandas Series with the KPI time series data.
    - selected_f: Selected seasonality frequency, used to segment the data into seasonal windows.
    - n_period: Number of iterations for trend drift detection, specifying how many times to check for drift.
    - send_alert_flag: function for sending alerts to API layer, True by default

    Returns:
    - trend_drift_flag: A boolean indicating if a trend drift is detected (True if drift is detected, False otherwise).
    """


    trend_drift_bool = False   # Flag to indicate if trend drift is detected
    ks_stat = 0                # Kolmogorov-Smirnov test statistic
    trend_drift = 0            # Direction of trend drift (positive or negative)

    # Check if time_series is long enough for comparison (at least twice the selected seasonality frequency)
    if len(time_series) > 2 * selected_f:
        i = 0
        # Iterate up to 'n_period' times to check for trend drift
        while i < n_period and not trend_drift_bool:
            # Perform the Kolmogorov-Smirnov test to compare the most recent seasonal period with previous periods
            if len(time_series) > (2 + i) * selected_f:
                seasonal_values = time_series[-(2 + i) * selected_f:-(1 + i) * selected_f]
                ks_stat, p_value = ks_2samp(time_series[-selected_f:], seasonal_values, method='asymp')

                # If the p-value is less than 0.05, trend drift is detected
                if p_value < 0.01:
                    trend_drift_bool = True
                    # Determine the direction of the trend drift based on the mean of the seasonal values
                    if seasonal_values.mean() < time_series[-selected_f:].mean():
                        trend_drift = i + 1
                        # Positive trend drift
                        # severity is set to high for all the trend drift, since they are considered of high relevance for the user
                        if send_alert_flag:
                            send_alert(streaming_data["machineID"], 'high', f'A positive trend drift was detected during the last {selected_f} samples, with respect to the previous {(i+1)*selected_f} samples', streaming_data["kpi"], streaming_data["aggr_type"], 'Positive_trend_drift', timestamp= streaming_data['current_timestamps'].iloc[-1])
                       
                    else:
                        trend_drift = -(i + 1)
                        # Negative trend drift
                        if send_alert_flag:
                            send_alert(streaming_data["machineID"], 'high', f'A negative trend drift was detected during the last {selected_f} samples, with respect to the previous {(i+1)*selected_f} samples', streaming_data["kpi"], streaming_data["aggr_type"], 'Negative_trend_drift', timestamp=streaming_data['current_timestamps'].iloc[-1])
                        
            i = i + 1

    # Return the trend drift detection result
    return trend_drift

# Note:
# The Kolmogorov-Smirnov (KS) test works best with at least 30 samples, so keep in mind that the detection found
# here might not be fully reliable but is suitable for triggering an alert.


def historical_concept_drift(streaming_data, time_series, selected_f, n = 4, send_alert_flag = True):
    """
    Detects historical concept drift by checking for trend drift at each point in the time series.
    This function applies the trend drift detection iteratively, using the data available up to each time point.

    Parameters:
    - streaming_data: dict with machineID, kpi, aggr_type and value
    - time_series: Pandas Series with the KPI time series data.
    - selected_f: Selected seasonality frequency used for detecting trend drift.
    - n: Number of iterations for trend drift detection, specifying how many times to check for drift.
    - send_alert_flag: function for sending alerts to API layer, True by default

    Returns:
    - trend_drift_h: An array with flags indicating if trend drift was detected at each time point.
    """
    trend_drift_h = np.zeros(len(time_series))  # Initialization of the drift detection array

    # Iterate through each point in the time series
    for i in range(len(time_series)):
        # Create a subseries up to the current point (i) for historical analysis
        h_time_series = time_series[:i]
        current_streaming_data = streaming_data.copy()
        current_streaming_data['current_timestamps'] = streaming_data["current_timestamps"].iloc[:i]

        # Apply trend drift detection recursively for the current subseries
        trend_drift_h[i] = detect_trend_drift_recursive(current_streaming_data, h_time_series, selected_f, n, send_alert_flag = send_alert_flag)

    # Return the array of trend drift detection results for the entire series
    return trend_drift_h


# HISTORICAL DATA PREPROCESSING
def preprocess_h_data(streaming_data, time_series, ex_lower_thr=None, ex_higher_thr=None, send_alert_flag = True):
    """
    Preprocesses historical time series data by handling missing values, analyzing seasonality,
    detecting inconsistencies, and identifying trend drift.

    Parameters:
    - streaming_data: dict with machineID, kpi, aggr_type and value
    - time_series: Pandas Series with the historical KPI time series data.
    - ex_lower_thr: Lower exogenous threshold for detecting inconsistencies (optional).
    - ex_higher_thr: Higher exogenous threshold for detecting inconsistencies (optional).
    - send_alert_flag: function for sending alerts to API layer, True by default


    Returns:
    - best_decomposition: Best seasonal decomposition result for the time series.
    - selected_f: Selected seasonality frequency for the time series.
    - inconsistencies_flag_vect: A flag array indicating inconsistencies based on thresholds.
    - h_trend_drift: An array of flags indicating trend drift at each time point.
    - time_series: Preprocessed time series with missing values handled.
    - imputation_mask: Mask showing which values were imputed.
    """
    
    # Initialize variables for the results of different analyses
    best_decomposition, selected_f, inconsistencies_flag_vect, h_trend_drift = None, None, None, None

    # Handle missing data and raise warning if needed
    time_series, imputation_mask = handle_missing_values_h(streaming_data, time_series, send_alert_flag = send_alert_flag)

    # If less than 15% of the data is missing, proceed with further analyses

    if imputation_mask.mean() < 0.15:
        # Perform seasonality analysis
        best_decomposition, selected_f = analysis_seasonality(time_series)

        # Perform statistical analysis (currently commented out)
        # data_parameters = perform_stat_analysis(time_series)

        # Detect inconsistencies in the data with respect to exogenous thresholds (anomalies/spikes)
        inconsistencies_flag_vect = detect_inconsistencies_exogenous(streaming_data, time_series, ex_lower_thr, ex_higher_thr, send_alert_flag = send_alert_flag)

        # Detect trend drift in the time series
        h_trend_drift = historical_concept_drift(streaming_data, time_series, selected_f, send_alert_flag = send_alert_flag)

    # Return the results from the preprocessing steps
    return best_decomposition, selected_f, inconsistencies_flag_vect, h_trend_drift, time_series, imputation_mask  # data_parameters (commented out)


def preprocess_entire_h_data(data, ex_thr_matrix, send_alert_flag=True):
    """
    Preprocesses the entire historical dataset for all KPIs, machines, and aggregation types.
    
    Steps include:
    - Validation of dataset consistency.
    - Seasonal decomposition of time series.
    - Detection of numerical inconsistencies based on exogenous thresholds.
    - Trend drift analysis.
    - Optional alert sending to an API layer.
    
    Parameters:
    - data: Pandas DataFrame containing historical data. Must include columns:
        'machineID', 'kpi', 'aggr_type' (e.g., 'sum', 'avg', 'max', 'min'), 
        'timestamp', and 'value'.
    - ex_thr_matrix: Pandas DataFrame containing exogenous thresholds for each 
        combination of 'machineID', 'kpi', and 'aggr_type'. Must include:
        'min_threshold' and 'max_threshold'.
    - send_alert_flag: Boolean flag to enable or disable alert sending. Default is True.

    Returns:
    - historical_data_analysis: Pandas DataFrame containing the analysis results 
      (residuals, trend_drift, value, and imputation) for each combination of 
      'machineID', 'kpi', and 'aggr_type', with timestamps.
    - seasonalities: Pandas DataFrame containing the seasonal frequencies 
      (`selected_f`) and the last timestamp (`timestamp`) for each combination of 'machineID', 'kpi', and 'aggr_type'.
    """
    # Step 1: Validate the consistency of the dataset
    #print('Checking invalid data')
    check_invalid_data(data)

    # Step 2: Initialize DataFrame for historical analysis
    names = data['machineID'].unique()
    kpis = data['kpi'].unique()
    cols = data['aggr_type'].unique()
    timestamps = data['timestamp'].unique()

    # Generate all possible combinations of 'machineID', 'kpi', 'aggr_type', and 'timestamp'
    combinations = list(product(names, kpis, cols, timestamps))
    historical_data_analysis = pd.DataFrame(combinations, columns=['machineID', 'kpi', 'aggr_type', 'timestamp'])
    historical_data_analysis['residuals'] = None
    historical_data_analysis['trend_drift'] = None
    historical_data_analysis['value'] = None
    historical_data_analysis['imputation'] = None

    # Step 3: Initialize DataFrame for seasonalities
    comb = list(product(names, kpis, cols))
    seasonalities = pd.DataFrame(comb, columns=['machineID', 'kpi', 'aggr_type'])
    seasonalities['selected_f'] = None
    seasonalities['timestamp'] = data['timestamp'].max()

    # Step 4: Process each combination of 'machineID', 'kpi', and 'aggr_type'
    c = 1
    for name in tqdm(names):
        print(f'Preprocessing:{c}/{len(names)}')
        c = c + 1 
        for kpi in kpis:
            for col in cols:
                # Extract the time series for the current combination
                time_series = data.loc[
                    (data['machineID'] == name) &
                    (data['kpi'] == kpi) &
                    (data['aggr_type'] == col), 'value'
                ]
                current_timestamps = data.loc[
                    (data['machineID'] == name) &
                    (data['kpi'] == kpi) &
                    (data['aggr_type'] == col), 'timestamp'
                ]

                # Retrieve thresholds for the current combination
                ex_lower_thr = ex_thr_matrix.loc[
                    (ex_thr_matrix['machineID'] == name) &
                    (ex_thr_matrix['kpi'] == kpi) &
                    (ex_thr_matrix['aggr_type'] == col), 'min_threshold'
                ].iloc[0] if not ex_thr_matrix.loc[
                    (ex_thr_matrix['machineID'] == name) &
                    (ex_thr_matrix['kpi'] == kpi) &
                    (ex_thr_matrix['aggr_type'] == col), 'min_threshold'
                ].empty else None

                ex_higher_thr = ex_thr_matrix.loc[
                    (ex_thr_matrix['machineID'] == name) &
                    (ex_thr_matrix['kpi'] == kpi) &
                    (ex_thr_matrix['aggr_type'] == col), 'max_threshold'
                ].iloc[0] if not ex_thr_matrix.loc[
                    (ex_thr_matrix['machineID'] == name) &
                    (ex_thr_matrix['kpi'] == kpi) &
                    (ex_thr_matrix['aggr_type'] == col), 'max_threshold'
                ].empty else None

                # Preprocess the time series
                best_decomposition, selected_f, inconsistencies_flag_vect, h_trend_drift, time_series, imputation_mask = preprocess_h_data(
                    {"machineID": name.astype(str), "kpi": kpi, "aggr_type": col, "current_timestamps": current_timestamps},
                    time_series,
                    ex_lower_thr,
                    ex_higher_thr,
                    send_alert_flag=send_alert_flag
                )

                if imputation_mask.mean() < 0.15:
                    # Convert results to lists
                    residuals_list = best_decomposition.resid.tolist()
                    trend_drift_list = h_trend_drift.tolist()
                    value_list = time_series.tolist()
                    imputation_list = imputation_mask.tolist()
                    timestamp_list = current_timestamps.tolist()

                    # Update historical_data_analysis
                    for i, timestamp in enumerate(timestamp_list):
                        historical_data_analysis.loc[
                            (historical_data_analysis['machineID'] == name) &
                            (historical_data_analysis['kpi'] == kpi) &
                            (historical_data_analysis['aggr_type'] == col) &
                            (historical_data_analysis['timestamp'] == timestamp), 
                            ['residuals', 'trend_drift', 'value', 'imputation']
                        ] = [residuals_list[i], trend_drift_list[i], value_list[i], imputation_list[i]]

                    # Update seasonalities
                    seasonalities.loc[
                        (seasonalities['machineID'] == name) &
                        (seasonalities['kpi'] == kpi) &
                        (seasonalities['aggr_type'] == col), 
                        'selected_f'
                    ] = selected_f

                    # Update the timestamp column with the last timestamp
                    seasonalities.loc[
                        (seasonalities['machineID'] == name) &
                        (seasonalities['kpi'] == kpi) &
                        (seasonalities['aggr_type'] == col), 
                        'timestamp'
                    ] = timestamp_list[-1]  # Set to the last timestamp


    # Return the DataFrames
    return historical_data_analysis, seasonalities 


# PREPROCESSING STREAMING DATA
def preprocess_s_data(streaming_data, value, time_series, imputation_mask, ex_lower_thr, ex_higher_thr, selected_f, send_alert_flag=True):
    """
    Preprocesses a single streaming data point, including handling missing values,
    detecting inconsistencies (anomalies/spikes), and identifying trend drift.

    Parameters:
    - streaming_data: dict with machineID, kpi, aggr_type and value
    - value: The most recently collected data point.
    - time_series: Pandas Series with the historical time series data for the KPI, machine, and column.
    - imputation_mask: Mask that indicates which values in the time series are missing.
    - ex_lower_thr: Lower threshold for detecting anomalies (optional).
    - ex_higher_thr: Higher threshold for detecting anomalies (optional).
    - selected_f: Selected seasonality frequency for the time series.
    - send_alert_flag: function for sending alerts to API layer, True by default

    Returns:
    - inconsistencies_flag: Flag indicating if the new value is inconsistent (anomalous) based on thresholds.
    - trend_drift: A flag indicating if trend drift is detected in the time series.
    - imp_value: The imputed value (if applicable) for the current data point.
    - imputation_bool: Flag indicating if the current data point was imputed.
    """

    # Handle missing data and raise warning if necessary
    imputation_bool, imp_value = handle_missing_values(streaming_data, value, time_series, imputation_mask, send_alert_flag = send_alert_flag)

    # Initialize default values for outputs
    inconsistencies_flag = None
    trend_drift = None

    # Function to check if imp_value is NaN (handles scalars and numpy arrays)
    def is_nan(value):
        if isinstance(value, (float, int)):
            return np.isnan(value)
        elif isinstance(value, np.ndarray):
            return np.isnan(value).all()
        return pd.isna(value)

    # Proceed only if imp_value is not NaN
    if not is_nan(imp_value):
        # Detect inconsistencies in the numerical values (anomalies or spikes)
        inconsistencies_flag = detect_inconsistencies_exogenous(
            streaming_data, 
            imp_value, 
            ex_lower_thr, 
            ex_higher_thr, 
            send_alert_flag = send_alert_flag)

        # Detect trend drift in the updated time series by including the most recent value
        trend_drift = detect_trend_drift_recursive(
            streaming_data,
            pd.concat([time_series, pd.Series([imp_value])], ignore_index=True),
            selected_f,
            send_alert_flag = send_alert_flag
        )

    # Return the results: flag for inconsistencies, trend drift, imputed value, and imputation status
    return inconsistencies_flag, trend_drift, imp_value, imputation_bool


