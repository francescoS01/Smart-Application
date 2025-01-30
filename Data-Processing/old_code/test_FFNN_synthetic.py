#Generate and show test series with 7 days seasonality
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prediction_functions import forecast_with_ffnn 


def generate_time_series_with_seasonality(length=365, seed=0):
    np.random.seed(seed)
    
    # Linear trend
    trend = np.linspace(0, 1, length)
    
    # Seasonal component
    seasonality = 0.3 * np.sin(2 * np.pi * np.arange(length) / 7)
    
    # Random noise
    noise = 0.1 * np.random.randn(length)
    
    # Resulting series
    time_series = trend + seasonality + noise
    
    # Creation of the series Dataframe
    dates = pd.date_range(start="2024-01-01", periods=length)
    df = pd.DataFrame({"value": time_series}, index=dates)
    
    return df

# Series generation
synthetic_series = generate_time_series_with_seasonality(length=365)

# Visualization of the series
plt.figure(figsize=(10, 6))
plt.plot(synthetic_series.index, synthetic_series["value"], label="Synthetic Series")
plt.title("Synthetic Time Series with Seasonality (7-day period)")
plt.xlabel("Date")
plt.ylabel("Value")
plt.grid()
plt.legend()
plt.show()

#Call the function with the synthetic series
#trained_ffnn, scaler = forecast_with_ffnn(synthetic_series, n_lags=14, epochs=100, batch_size=16, seed=0)

