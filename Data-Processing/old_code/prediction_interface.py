from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
from prediction_functions import forecast_future, forecast_with_ffnn  # Import your functions
import pickle  # For model serialization/deserialization
import os  # To handle file paths

# Initialize FastAPI app
app = FastAPI()

# Directory to store and retrieve pickle files
PICKLE_DIR = "models/"  # Ensure this directory exists and is writable

# Request model for simple KPI
class SimpleKPIRequest(BaseModel):
    machine: str
    kpi_name: str
    aggr_type: str  # Aggregation type
    n_future: int = 21

# Request model for complex KPI
class ComplexKPIRequest(BaseModel):
    machine: str
    kpi_name: str
    aggr_type: str  # Aggregation type
    time_series: list[float]
    dates: list[str]
    n_future: int = 21

def get_model_from_pickle(machine: str, kpi_name: str, aggr_type: str):
    """
    Retrieve the trained model and scaler from a pickle file.

    Parameters:
    - machine (str): The name of the machine.
    - kpi_name (str): The name of the KPI.
    - aggr_type (str): The aggregation type.

    Returns:
    - model (object): The trained FFNN model.
    - scaler (object): The scaler used during training.
    """
    try:
        model_path = os.path.join(PICKLE_DIR, f"{machine}_{kpi_name}_{aggr_type}_model.pkl")
        scaler_path = os.path.join(PICKLE_DIR, f"{machine}_{kpi_name}_{aggr_type}_scaler.pkl")

        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            raise FileNotFoundError("Model or scaler file not found.")

        # Load model and scaler
        with open(model_path, "rb") as model_file, open(scaler_path, "rb") as scaler_file:
            model = pickle.load(model_file)
            scaler = pickle.load(scaler_file)

        return model, scaler

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

@app.get("/forecast-simple")
def forecast_simple(request: SimpleKPIRequest):
    try:
        # Retrieve the model and scaler
        model, scaler = get_model_from_pickle(request.machine, request.kpi_name, request.aggr_type)

        # Generate future predictions
        predictions_rescaled = forecast_future(
            time_series=None,
            trained_ffnn=model,
            scaler=scaler,
            n_future=request.n_future,
            n_lags=14,
            plot_results=False
        )

        # Get the first predicted value
        first_prediction = predictions_rescaled[0]  # The first predicted value
        first_prediction_date = pd.Timestamp.now(tz="UTC")  # The date for the first prediction

        # Upload the first prediction to the Feature Store
        upload_first_step_to_feature_store(
            feature_store_client=feature_store_client,  # Replace with actual client
            feature_group_name="machine_kpi_predictions",  # Replace with actual feature group name
            machine=request.machine,
            kpi_name=request.kpi_name,
            aggr_type=request.aggr_type,
            prediction=first_prediction,
            date=first_prediction_date
        )

        return {
            "machine": request.machine,
            "kpi_name": request.kpi_name,
            "aggr_type": request.aggr_type,
            "first_prediction": first_prediction
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    """
    Root endpoint to confirm the API is running.
    """
    return {"message": "API is running. Use the /forecast-simple or /forecast-complex endpoints."}


@app.post("/forecast-complex")
def forecast_complex(request: ComplexKPIRequest):
    try:
        # Prepare the time series as a pandas DataFrame
        time_series_df = pd.DataFrame({
            "date": pd.to_datetime(request.dates),
            "value": request.time_series
        }).set_index("date")

        # Train a new model
        model, scaler = forecast_with_ffnn(
            time_series=time_series_df["value"],
            n_lags=14,
            hidden_units_options=[32, 64, 128],
            epochs=50,
            batch_size=16,
            seed=0,
            plot_results=False
        )

        # Generate future predictions
        predictions_rescaled = forecast_future(
            time_series=time_series_df["value"],
            trained_ffnn=model,
            scaler=scaler,
            n_future=request.n_future,
            n_lags=14,
            plot_results=False
        )

        # Get the first predicted value
        first_prediction = predictions_rescaled[0]  # The first predicted value
        first_prediction_date = pd.Timestamp.now(tz="UTC")  # The date for the first prediction

        # Upload the first prediction to the Feature Store
        upload_first_step_to_feature_store(
            feature_store_client=feature_store_client,  # Replace with actual client
            feature_group_name="machine_kpi_predictions",  # Replace with actual feature group name
            machine=request.machine,
            kpi_name=request.kpi_name,
            aggr_type=request.aggr_type,
            prediction=first_prediction,
            date=first_prediction_date
        )

        return {
            "machine": request.machine,
            "kpi_name": request.kpi_name,
            "aggr_type": request.aggr_type,
            "first_prediction": first_prediction
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/forecast-complex")
def forecast_complex(request: ComplexKPIRequest):
    """
    Train a model and forecast future values for a complex KPI.

    Parameters:
    - machine (str): The machine name.
    - kpi_name (str): The KPI name.
    - aggr_type (str): The aggregation type.
    - time_series (list[float]): The historical values.
    - dates (list[str]): Corresponding dates for the time series.
    - n_future (int): Number of future values to predict.

    Returns:
    - dict: Predicted values and confidence intervals.
    """
    try:
        # Prepare the time series as a pandas DataFrame
        time_series_df = pd.DataFrame({
            "date": pd.to_datetime(request.dates),
            "value": request.time_series
        }).set_index("date")

        # Train a new model
        model, scaler = forecast_with_ffnn(
            time_series=time_series_df["value"],
            n_lags=14,
            hidden_units_options=[32, 64, 128],
            epochs=50,
            batch_size=16,
            seed=0,
            plot_results=False
        )

        # Save the trained model and scaler to pickle files
        model_path = os.path.join(PICKLE_DIR, f"{request.machine}_{request.kpi_name}_{request.aggr_type}_model.pkl")
        scaler_path = os.path.join(PICKLE_DIR, f"{request.machine}_{request.kpi_name}_{request.aggr_type}_scaler.pkl")

        with open(model_path, "wb") as model_file, open(scaler_path, "wb") as scaler_file:
            pickle.dump(model, model_file)
            pickle.dump(scaler, scaler_file)

        # Generate future predictions
        predictions_rescaled = forecast_future(
            time_series=time_series_df["value"],
            trained_ffnn=model,
            scaler=scaler,
            n_future=request.n_future,
            n_lags=14,
            plot_results=False
        )

        return {
            "machine": request.machine,
            "kpi_name": request.kpi_name,
            "aggr_type": request.aggr_type,
            "predictions": predictions_rescaled.tolist()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
