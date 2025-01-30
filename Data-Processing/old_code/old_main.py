# main of the processing 

## Libraries and import data
"""

# General libraries
import os
import random
import warnings

# Libraries for data analysis and manipulation
import numpy as np
import pandas as pd

# Libraries for machine learning and preprocessing
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    mean_absolute_percentage_error,
)
from sklearn.ensemble import IsolationForest
from itertools import product

# Libraries for visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Libraries for time series analysis
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Libraries for statistical analysis
from scipy.stats import ks_2samp, shapiro

# Libraries for neural networks and TensorFlow
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense


# pipeline historical 

# Definisci le colonne e il numero di righe
columns = ['name', 'kpi', 'col', 'ex_lower_thr', 'ex_higher_thr']
num_rows = 896

# Crea il DataFrame con valori inizializzati a None
ex_thr_matrix = pd.DataFrame(None, index=range(num_rows), columns=columns)

# dataframe with residuals from decomposition analysis

names = data['name'].unique()
kpis = data['kpi'].unique()
cols = ['sum', 'avg', 'min', 'max']

# generate all possible combinations
combinations = list(product(names, kpis, cols))

residuals_df = pd.DataFrame(combinations, columns=['name', 'kpi', 'col'])
residuals_df['residuals'] = None

## PIPELINE HISTORICAL DATA

h_data = data
# checking consistency rules on the whole dataset
#check_invalid_data(h_data)

# preprocessing data on single time series
for name in h_data['name'].unique():
    for k in h_data['kpi'].unique():
        for col in h_data.columns[4:]: # sum,avg,max,min
          time_series = h_data.loc[(h_data['name'] == name) & (h_data['kpi'] == k), col]
          ex_lower_thr = ex_thr_matrix[(ex_thr_matrix['name'] == name) & (ex_thr_matrix['kpi'] == k) & (ex_thr_matrix['col'] == col)]['ex_lower_thr'].iloc[0] if not ex_thr_matrix[(ex_thr_matrix['name'] == name) & (ex_thr_matrix['kpi'] == k) & (ex_thr_matrix['col'] == col)]['ex_lower_thr'].empty else None
          ex_higher_thr = ex_thr_matrix[(ex_thr_matrix['name'] == name) & (ex_thr_matrix['kpi'] == k) & (ex_thr_matrix['col'] == col)]['ex_higher_thr'].iloc[0] if not ex_thr_matrix[(ex_thr_matrix['name'] == name) & (ex_thr_matrix['kpi'] == k) & (ex_thr_matrix['col'] == col)]['ex_higher_thr'].empty else None
          best_decomposition, selected_f, inconsistencies_flag_vect, h_trend_drift, time_series, imputation_mask = preprocess_h_data(time_series, ex_lower_thr, ex_higher_thr)
          #h_data.loc[(h_data['name'] == name) & (h_data['kpi'] == k), col] = time_series
          residuals_df.at[residuals_df.loc[(residuals_df['name'] == name) & (residuals_df['kpi'] == k) & (residuals_df['col'] == col)].index[0], 'residuals'] = best_decomposition.resid


# to save:
## we need to call the save function for inconsistencies_flag_vect, h_trend_drift, time_series, imputation_mask iterating on time
## we need to call the save function only once to save the selected frequency
## best_decomposition is not stored in the feature store but is only used to train the iso_forest models


pp_data = data # original dataset structure preprocessed
s_data = pp_data[pp_data['time'] == '2024-10-19T00:00:00Z']

# Definisci le colonne e il numero di righe
columns = ['name', 'kpi', 'col', 'ex_lower_thr', 'ex_higher_thr']
num_rows = 896

# Crea il DataFrame con valori inizializzati a None
ex_thr_matrix = pd.DataFrame(None, index=range(num_rows), columns=columns)

pp_data = data # original dataset structure preprocessed
s_data = pp_data[pp_data['time'] == '2024-10-19T00:00:00Z'] # we are taking the last day as example of streaming data
## maybe could be used the new data structure (in case change the inner cycle)

# preprocessing data on single time series
for name in pp_data['name'].unique():
    for k in pp_data['kpi'].unique():
        for col in pp_data.columns[4:]: # sum,avg,max,min
          time_series = pp_data.loc[(pp_data['name'] == name) & (pp_data['kpi'] == k), col]
          new_value = s_data.loc[(s_data['name'] == name) & (s_data['kpi'] == k), col]
          ex_lower_thr = ex_thr_matrix[(ex_thr_matrix['name'] == name) & (ex_thr_matrix['kpi'] == k) & (ex_thr_matrix['col'] == col)]['ex_lower_thr'].iloc[0] if not ex_thr_matrix[(ex_thr_matrix['name'] == name) & (ex_thr_matrix['kpi'] == k) & (ex_thr_matrix['col'] == col)]['ex_lower_thr'].empty else None
          ex_higher_thr = ex_thr_matrix[(ex_thr_matrix['name'] == name) & (ex_thr_matrix['kpi'] == k) & (ex_thr_matrix['col'] == col)]['ex_higher_thr'].iloc[0] if not ex_thr_matrix[(ex_thr_matrix['name'] == name) & (ex_thr_matrix['kpi'] == k) & (ex_thr_matrix['col'] == col)]['ex_higher_thr'].empty else None
          selected_f = feat_data[(feat_data['name'] == name) & (feat_data['kpi'] == k) & (feat_data['col'] == col)]['selected_f'].iloc[0]
          imputation_mask = feat_data[(feat_data['name'] == name) & (feat_data['kpi'] == k) & (feat_data['col'] == col)]['imputation_mask'].iloc[0]
          inconsistencies_flag, trend_drift, imp_value, imputation_bool = preprocess_s_data(new_value, time_series, imputation_mask, ex_lower_thr, ex_higher_thr, selected_f)

# to save:
## we need to call the save function only once to save inconsistencies_flag, trend_drift, imp_value, imputation_bool


ANOMALIES: 
"""### Model training on historical data"""

# Extracting the residuals for each combination
for name in residuals_df['name'].unique():
    for k in residuals_df['kpi'].unique():
        for col in residuals_df['col'].unique(): # sum,avg,max,min
            residuals = residuals_df.at[residuals_df.loc[(residuals_df['name'] == name) & (residuals_df['kpi'] == k) & (residuals_df['col'] == col)].index[0], 'residuals']
            anomaly_indices, iso_forest = detect_anomalies_from_decomposition(residuals, contamination = 0.04)
            anomalies = pd.Series(0, index=range(len(time_series)))
            anomalies.loc[anomaly_indices] = 1


# to save
## we need to call the save function only once to save the iso_forest model
## we need to call the save function for anomalies iterating on time

# ANOMALIES IN STREAMING 

# required inputs
current_value = None
predicted_value = None
iso_forest

# Compute the prediction error
prediction_error = -200000#current_value - predicted_value

# Anomaly detection on streaming data
anomaly_bool = detect_anomalies_from_streaming_data(prediction_error, iso_forest)
print(anomaly_bool)

# FROM THE FEATURE STORE 
#trial
for name in feat_s_data['name'].unique():
    for k in feat_s_data['kpi'].unique():
        for col in feat_s_data['col'].unique():
          current_value = feat_s_data[(feat_s_data['name'] == name) & (feat_s_data['kpi'] == k) & (feat_s_data['col'] == col)]['current_value'].iloc[0]
          predicted_value = feat_s_data[(feat_s_data['name'] == name) & (feat_s_data['kpi'] == k) & (feat_s_data['col'] == col)]['predicted_value'].iloc[0]
          iso_forest = feat_s_data[(feat_s_data['name'] == name) & (feat_s_data['kpi'] == k) & (feat_s_data['col'] == col)]['iso_forest'].iloc[0]
          prediction_error = current_value - predicted_value
          anomaly_bool = detect_anomalies_from_streaming_data(prediction_error, iso_forest)
          # anomaly bool to be stored


# PREDICTION 

"""### Model training on historical data

Here we are training the prediction models ( using FFNN ) for the time series associated to the selected KPIs and machines
"""

# Extracting the time_series for each combination
for name in feat_data['name'].unique():
    for k in feat_data['kpi'].unique():
        for col in feat_data['col'].unique():
            # Filter the dataframe to get the corresponding row
            time_series = feat_data[(feat_data['name'] == name) &
                                   (feat_data['kpi'] == k) &
                                   (feat_data['col'] == col)]['time_series']
            time_series = pd.DataFrame({'value': time_series.tolist()[0]}, index = data['time'].unique())

            # Pass the time_series to the detect anomalies function
            trained_ffnn = forecast_with_ffnn(time_series)


  # Extracting the time_series for each combination
for name in feat_data['name'].unique():
    for k in feat_data['kpi'].unique():
        for col in feat_data['col'].unique():
            # Filter the dataframe to get the corresponding row
            time_series = feat_data[(feat_data['name'] == name) &
                                   (feat_data['kpi'] == k) &
                                   (feat_data['col'] == col)]['time_series']
            time_series = pd.DataFrame({'value': time_series.tolist()[0]}, index = data['time'].unique())
            trained_ffnn = feat_s_data[(feat_s_data['name'] == name) & (feat_s_data['kpi'] == k) & (feat_s_data['col'] == col)]['trained_ffnn'].iloc[0]
            scaler = feat_s_data[(feat_s_data['name'] == name) & (feat_s_data['kpi'] == k) & (feat_s_data['col'] == col)]['scaler'].iloc[0]

            # Pass the time_series to the predict future values
            predicted_values = forecast_future(time_series, trained_ffnn, scaler)

            ## remember to save the predicted values in place of the previous ones in the database
            ## for the integration part could be possible to substitute the complete time_series with only an array containing
            ## the last n_lags values of it saved in the feat_s_data
