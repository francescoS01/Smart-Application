"""
This script defines functions for forecasting future values of a Key Performance Indicator (KPI) time series using a 
Feedforward Neural Network (FFNN). It includes several components:

1. `forecast_with_ffnn`: A function to train an FFNN on historical KPI data, performing hyperparameter tuning, 
   scaling, and preparing the data with lagged inputs. It also evaluates the model performance and stores the trained 
   model, scaler, and residuals for later use.

2. `forecast_future`: A function that uses a trained FFNN model to forecast future values for a given time series, 
   along with growing confidence intervals that expand as the forecast horizon increases.

3. `forecast_from_dataframe`: A function that iterates over a DataFrame containing time series data for multiple 
   machines, KPIs, and aggregation types. It calls `forecast_with_ffnn` for each group with minimal imputation and 
   stores the forecasted values and confidence intervals back into the DataFrame.

The script is designed for use in a predictive maintenance or KPI monitoring context, where accurate forecasting of future 
trends and associated uncertainty is essential. The models are saved to disk, and the results are visualized for easy 
interpretation.
"""

# Importing required libraries
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import os
import pickle
import random

"""### FFNN model"""

def forecast_with_ffnn(
    streaming_data, time_series, n_lags=14, hidden_units_options=[32, 64, 128], epochs=50, batch_size=16, seed=0, plot_results=True
):
    """
    Forecast future values of a KPI time series using a Feedforward Neural Network (FFNN).
    
    Parameters:
    - streaming_data (dict): Contains metadata like 'machineID', 'kpi', and 'aggr_type' for saving the model.
    - time_series (pd.Series): Time series data of the KPI with datetime index.
    - n_lags (int): The number of lagged time steps to consider as input features for the model (default is 14).
    - hidden_units_options (list): A list of different numbers of hidden units to test for the FFNN model (default is [32, 64, 128]).
    - epochs (int): Number of training epochs (default is 50).
    - batch_size (int): Batch size for training the model (default is 16).
    - seed (int): Random seed for reproducibility (default is 0).
    - plot_results (bool): Whether to plot the training, validation, test results, and confidence intervals (default is True).
    
    Returns:
    - model (tensorflow.keras.models.Sequential): The trained FFNN model.
    - scaler (sklearn.preprocessing.MinMaxScaler): The scaler used to scale the data.
    - std_residuals (float): Standard deviation of residuals on the test set.
    
    The function trains the FFNN model on the time series data, performs hyperparameter tuning, and predicts future values.
    """
    
    # Set seed for reproducibility
    np.random.seed(seed)
    tf.random.set_seed(seed)
    random.seed(seed)

    # Ensure time series is ordered and has no missing values
    time_series = time_series.dropna()
    time_series = time_series.sort_index()

    # Split the time series into training, validation, and test sets
    train_size = int(len(time_series) * 0.7)
    val_size = int(len(time_series) * 0.2)
    test_size = len(time_series) - train_size - val_size

    train = time_series.iloc[:train_size]
    validation = time_series.iloc[train_size:train_size + val_size]
    test = time_series.iloc[train_size + val_size:]

    # Scale the data using MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    train_scaled = scaler.fit_transform(train)
    validation_scaled = scaler.transform(validation)
    test_scaled = scaler.transform(test)
    train_val_scaled = np.vstack([train_scaled, validation_scaled])

    # Prepare the data by creating sliding windows for features and labels
    def prepare_data(series, n_lags):
        series = np.array(series)
        X = np.lib.stride_tricks.sliding_window_view(series, window_shape=n_lags)[:-1]
        y = series[n_lags:]
        return X, y

    # Prepare training, validation, and test data
    X_train_val, y_train_val = prepare_data(train_val_scaled.flatten(), n_lags)
    X_test, y_test = prepare_data(test_scaled.flatten(), n_lags)

    # Split into train and validation sets
    split_idx = len(train)
    X_train, y_train = X_train_val[:split_idx-n_lags], y_train_val[:split_idx-n_lags]
    X_val, y_val = X_train_val[split_idx-n_lags:], y_train_val[split_idx-n_lags:]

    # Reshape data to fit the model input shape
    X_train = X_train.reshape(X_train.shape[0], n_lags)
    X_val = X_val.reshape(X_val.shape[0], n_lags)
    X_test = X_test.reshape(X_test.shape[0], n_lags)

    # Hyperparameter tuning by testing different hidden layer sizes
    best_rmse = float('inf')
    best_units = None
    for units in hidden_units_options:
        model = Sequential([
            Dense(units, activation='relu', input_dim=n_lags),
            Dense(units // 2, activation='relu'),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)

        # Validate the model
        y_val_pred = model.predict(X_val).ravel()
        y_val_rescaled = scaler.inverse_transform(y_val.reshape(-1, 1)).ravel()
        y_val_pred_rescaled = scaler.inverse_transform(y_val_pred.reshape(-1, 1)).ravel()
        rmse = np.sqrt(mean_squared_error(y_val_rescaled, y_val_pred_rescaled))

        if rmse < best_rmse:
            best_rmse = rmse
            best_units = units

    # Final model training with the best hyperparameters
    model = Sequential([
        Dense(best_units, activation='relu', input_dim=n_lags),
        Dense(best_units // 2, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train_val, y_train_val, epochs=epochs, batch_size=batch_size, verbose=0)

    # Predict on test data
    y_test_pred = model.predict(X_test).ravel()
    y_test_rescaled = scaler.inverse_transform(y_test.reshape(-1, 1)).ravel()
    y_test_pred_rescaled = scaler.inverse_transform(y_test_pred.reshape(-1, 1)).ravel()

    # Sliding window predictions
    predictions = []
    input_seq = X_test[0]
    for _ in range(len(test)):
        pred = model.predict(input_seq.reshape(1, -1), verbose=0)[0, 0]
        predictions.append(pred)
        input_seq = np.append(input_seq[1:], pred)

    predictions_rescaled = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()

    # Calculate residuals and confidence interval
    residuals = y_test_rescaled.flatten() - y_test_pred_rescaled
    std_residuals = np.std(residuals)
    confidence_interval = (predictions_rescaled - 2 * std_residuals, predictions_rescaled + 2 * std_residuals)

    # Plot results if required
    if plot_results:
        plt.figure(figsize=(8, 4))
        plt.plot(pd.to_datetime(time_series.index), time_series['value'], label='Full Series', color='gray', linestyle='--', alpha=0.5)
        plt.plot(pd.to_datetime(train.index), train['value'], label='Train', color='blue')
        plt.plot(pd.to_datetime(validation.index), validation['value'], label='Validation', color='green')
        plt.plot(pd.to_datetime(test.index), test['value'], label='Test', color='red')
        plt.plot(pd.to_datetime(test.index), predictions_rescaled, label='Forecast', color='orange')
        plt.fill_between(
            test.index,
            predictions_rescaled - 2 * std_residuals,
            predictions_rescaled + 2 * std_residuals,
            color='orange', alpha=0.2, label='Confidence Interval'
        )
        plt.title('FFNN Forecast with Train, Validation, Test, and Confidence Interval')
        plt.xlabel('Time')
        plt.ylabel('Consumption')
        plt.legend()
        plt.grid()
        plt.show()

    # Save the model, scaler, and std_residuals to disk
    output_dir = "saved_ffnn_model"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f'ffnn_model_{streaming_data["machineID"]}_{streaming_data["kpi"]}_{streaming_data["aggr_type"]}.pkl')
    with open(filename, 'wb') as f:
        pickle.dump({'model': model, 'scaler': scaler, 'std_residuals': std_residuals}, f)

    return model, scaler, std_residuals


"""### Prediction of future values

Here we use the trained model to predict the future values \
The function is called once a day when we receive the new data, and the new predictions will substitute the previous ones
"""

def forecast_future(time_series, trained_ffnn, scaler, std_residuals, n_future=28, n_lags=14, plot_results=True):
    """
    Forecast future values of the time series using the trained FFNN model, with a growing confidence interval.

    Parameters:
    - time_series (pd.Series): The input time series for which predictions are to be made.
    - trained_ffnn (tensorflow.keras.models.Sequential): The trained FFNN model for forecasting.
    - scaler (sklearn.preprocessing.MinMaxScaler): The scaler used for scaling the data during training.
    - std_residuals (float): The standard deviation of the residuals for confidence interval calculation.
    - n_future (int): The number of future time steps to predict (default is 28).
    - n_lags (int): The number of previous time steps to use as input (default is 14).
    - plot_results (bool): Whether to plot the results with confidence intervals (default is True).

    Returns:
    - predictions_rescaled (numpy.array): The rescaled future predictions.
    - confidence_interval_lower_rescaled (numpy.array): The lower bound of the confidence interval.
    - confidence_interval_upper_rescaled (numpy.array): The upper bound of the confidence interval.
    """
    # Prepare the last window of the time series for prediction
    input_seq = time_series[-n_lags:].values
    input_seq_scaled = scaler.transform(input_seq.reshape(-1, 1)).flatten()

    # Initialize lists to store predictions and confidence intervals
    predictions = []
    confidence_interval_lower_all = []
    confidence_interval_upper_all = []

    for i in range(n_future):
        pred = trained_ffnn.predict(input_seq_scaled.reshape(1, -1), verbose=0)[0, 0]
        predictions.append(pred)
        
        # Append the new prediction to the sequence
        input_seq_scaled = np.append(input_seq_scaled[1:], pred)

        # Gradually increase the confidence interval as the forecast horizon grows
        std_residual_increase = std_residuals * (1 + 0.003 * i)  # Increase the std deviation by a small percentage

        # Calculate the confidence interval for this step
        confidence_interval_lower_all.append(pred - 2 * std_residual_increase)
        confidence_interval_upper_all.append(pred + 2 * std_residual_increase)

    # Rescale predictions and confidence intervals
    predictions_rescaled = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
    confidence_interval_lower_rescaled = scaler.inverse_transform(np.array(confidence_interval_lower_all).reshape(-1, 1)).flatten()
    confidence_interval_upper_rescaled = scaler.inverse_transform(np.array(confidence_interval_upper_all).reshape(-1, 1)).flatten()

    if plot_results:
        plt.figure(figsize=(8, 4))
        plt.plot(time_series.index, time_series.values, label='Historical Data', color='blue')
        future_dates = pd.date_range(time_series.index[-1], periods=n_future + 1, freq='D')[1:]
        plt.plot(future_dates, predictions_rescaled, label='Forecasted Values', color='orange')
        plt.fill_between(future_dates, confidence_interval_lower_rescaled, confidence_interval_upper_rescaled, color='orange', alpha=0.2, label='Confidence Interval')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title('Future Value Forecast with Confidence Interval')
        plt.legend()
        plt.show()

    return predictions_rescaled, confidence_interval_lower_rescaled, confidence_interval_upper_rescaled


def forecast_from_dataframe(df, n_lags=14, n_future=28, hidden_units_options=[32, 64, 128], epochs=50, batch_size=16, seed=0, plot_results=True):
    """
    Iterate through the DataFrame and call forecast_with_ffnn for each combination of
    'machineID', 'kpi', and 'aggr_type' where most of the 'imputation' values are non-null.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing the data. Must include 'timestamp', 'value', and 'imputation'.
    - n_lags (int): Number of lagged time steps to consider as input features for the model (default is 14).
    - n_future (int): Number of future time steps to forecast (default is 28).
    - hidden_units_options (list): List of hidden layer sizes to test (default is [32, 64, 128]).
    - epochs (int): Number of training epochs (default is 50).
    - batch_size (int): Batch size for training the model (default is 16).
    - seed (int): Random seed for reproducibility (default is 0).
    - plot_results (bool): If True, plots the training, validation, test results, and confidence intervals (default is True).

    Returns:
    - pd.DataFrame: Updated DataFrame with columns for next_days_predictions, confidence_interval_lower, and confidence_interval_upper.
    """
    # Group by 'machineID', 'kpi', and 'aggr_type'
    grouped = df.groupby(['machineID', 'kpi', 'aggr_type'])

    # Create new columns for storing predictions and confidence intervals
    df['next_days_predictions'] = None
    df['confidence_interval_lower'] = None
    df['confidence_interval_upper'] = None

    for (machineID, kpi, aggr_type), group in grouped:
        # Check if the average of 'imputation' is less than 0.15
        imputation_mean = group['imputation'].mean()

        if imputation_mean < 0.15:  # If the majority of values are not imputed
            # Ensure the 'value' column is sorted by 'timestamp'
            group = group.sort_values(by='timestamp')
            time_series = group.set_index('timestamp')['value']

            streaming_data = {
                'machineID': machineID,
                'kpi': kpi,
                'aggr_type': aggr_type
            }

            # Call forecast_with_ffnn to get the trained model and scaler
            trained_ffnn, scaler, std_residuals = forecast_with_ffnn(
                streaming_data=streaming_data,
                time_series=time_series,
                n_lags=n_lags,
                hidden_units_options=hidden_units_options,
                epochs=epochs,
                batch_size=batch_size,
                seed=seed,
                plot_results=plot_results
            )

            # Use the model and scaler to forecast future values
            predictions_rescaled, confidence_lower, confidence_upper = forecast_future(
                time_series=time_series,
                trained_ffnn=trained_ffnn,
                scaler=scaler,
                std_residuals=std_residuals,
                n_future=n_future,
                n_lags=n_lags,
                plot_results=plot_results
            )

            # Update the DataFrame with the forecasted values and confidence intervals
            last_timestamp = group['timestamp'].iloc[-1]
            df.loc[df['timestamp'] == last_timestamp, 'next_days_predictions'] = [predictions_rescaled.to_numpy()]
            df.loc[df['timestamp'] == last_timestamp, 'confidence_interval_lower'] = [confidence_lower.to_numpy()]
            df.loc[df['timestamp'] == last_timestamp, 'confidence_interval_upper'] = [confidence_upper.to_numpy()]

    return df


