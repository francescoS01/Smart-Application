"""
This script implements a pipeline for time-series forecasting using a feed-forward neural network (FFNN).
It includes the following steps:
1. Data preprocessing: Converts raw historical data into a structured format for time-series analysis.
2. Model training: Trains predictive models for each KPI and asset ID, saving the models for future use.
3. Model prediction: Loads pre-trained models and forecasts future values for specific KPIs and asset IDs.
"""

import pickle
import os
import pandas as pd
from Data_Processing.prediction_functions import forecast_future, forecast_with_ffnn


# 1. Data Preprocessing
def convert_h_data(h_data, aggregation='daily'):
    """
    Preprocess h_data to create time series for each unique combination of KPI, machine asset_id, and aggregation type.

    Parameters:
    - h_data (pd.DataFrame): Input DataFrame containing time-series data.
    - aggregation (str): Aggregation frequency ('daily', 'hourly', etc.).

    Returns:
    - dict: A dictionary where keys are tuples (kpi, asset_id, aggr_type), and values are pandas Series.
    """
    h_data['time'] = pd.to_datetime(h_data['time'])
    h_data = h_data.set_index('time')
    preprocessed_data = {}

    # Define the aggregation columns to process
    aggr_columns = ['sum', 'avg', 'min', 'max']
    for aggr_type in aggr_columns:
        filtered_data = h_data[['asset_id', 'kpi', aggr_type]].dropna()
        grouped = filtered_data.groupby(['asset_id', 'kpi'])

        # Group data by asset_id and KPI, then resample based on the specified aggregation
        for (asset_id, kpi), group in grouped:
            if aggregation == 'daily':
                series = group[aggr_type].resample('D').sum()
            elif aggregation == 'hourly':
                series = group[aggr_type].resample('H').sum()
            else:
                raise ValueError(f"Unsupported aggregation type: {aggregation}")
            series = series.dropna()
            preprocessed_data[(kpi, asset_id, aggr_type)] = series

    return preprocessed_data


# 2. Model Training
def train_and_save_models(preprocessed_data, n_lags, output_dir="saved_models"):
    """
    Train and save models for all combinations of KPI, asset_id, and aggregation type in the preprocessed data.

    Parameters:
    - preprocessed_data (dict): Preprocessed time-series data.
    - n_lags (int): Number of lag values to use for training.
    - output_dir (str): Directory to save the trained models.

    Returns:
    - int: Number of models successfully trained and saved.
    """
    os.makedirs(output_dir, exist_ok=True)
    training_count = 0

    for (kpi, asset_id, aggr_type), time_series in preprocessed_data.items():
        # Ensure sufficient data points exist for training
        if len(time_series) > n_lags:
            time_series_df = pd.DataFrame({'value': time_series.values}, index=time_series.index)
            training_count += 1
            plot_results = (training_count % 10 == 0)  # Plot results periodically

            # Train the FFNN model with specified parameters
            model, scaler = forecast_with_ffnn(
                time_series_df,
                n_lags=n_lags,
                hidden_units_options=[32, 64, 128],
                epochs=50,
                batch_size=16,
                seed=42,
                plot_results=plot_results
            )

            # Save the trained model and scaler to a file
            model_filename = os.path.join(output_dir, f"model_{asset_id}_{kpi}_{aggr_type}.pkl")
            with open(model_filename, 'wb') as f:
                pickle.dump({'model': model, 'scaler': scaler}, f)

            print(f"Model for KPI '{kpi}', asset_id '{asset_id}', aggregation '{aggr_type}' saved.")

    return training_count


# 3. Model Prediction
def load_and_predict(preprocessed_data, target_asset_id, target_kpi, n_lags, future_steps, output_dir="saved_models"):
    """
    Load saved models and make predictions for the specified asset_id and KPI.

    Parameters:
    - preprocessed_data (dict): Preprocessed time-series data.
    - target_asset_id (str): Asset ID to predict for.
    - target_kpi (str): KPI to predict for.
    - n_lags (int): Number of lag values used during training.
    - future_steps (int): Number of future steps to predict.
    - output_dir (str): Directory containing saved models.

    Returns:
    - None
    """
    for aggr_type in ['sum', 'avg', 'min', 'max']:
        model_filename = os.path.join(output_dir, f"model_{target_asset_id}_{target_kpi}_{aggr_type}.pkl")

        if os.path.exists(model_filename):
            # Load the saved model and scaler
            with open(model_filename, 'rb') as f:
                saved_data = pickle.load(f)

            model = saved_data['model']
            scaler = saved_data['scaler']
            print(f"Loaded model for asset_id '{target_asset_id}', aggregation '{aggr_type}'.")

            # Check if data exists for the specified combination
            if (target_kpi, target_asset_id, aggr_type) in preprocessed_data:
                # Generate future predictions
                predictions = forecast_future(
                    time_series=preprocessed_data[(target_kpi, target_asset_id, aggr_type)],
                    trained_ffnn=model,
                    scaler=scaler,
                    n_future=future_steps,
                    n_lags=n_lags,
                    plot_results=True
                )
                print(f"Future predictions for asset_id '{target_asset_id}', aggregation '{aggr_type}' completed.")
            else:
                print(f"No data for KPI '{target_kpi}', asset_id '{target_asset_id}', aggregation '{aggr_type}'.")
        else:
            print(f"Model for asset_id '{target_asset_id}', aggregation '{aggr_type}' not found.")


# 4. Main Function
def main_prediction():
    """
    Main function to preprocess data, train models, and make predictions.
    """
    h_data = load_preprocessed_data()  # Load the preprocessed data from an external source
    n_lags = 14
    future_steps = 21

    print("Starting preprocessing...")
    preprocessed_data = convert_h_data(h_data)
    print(f"Preprocessed {len(preprocessed_data)} time series.")

    print("Training models...")
    model_count = train_and_save_models(preprocessed_data, n_lags)
    print(f"Training completed. {model_count} models trained and saved.")

    # Uncomment the following lines to make predictions for a specific asset_id and KPI
    # print("Generating predictions...")
    # target_asset_id = "your_target_asset_id"  # Replace with your target asset_id
    # target_kpi = "your_target_kpi"  # Replace with your target KPI
    # load_and_predict(preprocessed_data, target_asset_id, target_kpi, n_lags, future_steps)


# Entry Point
if __name__ == "__main__":
    main_prediction()
