def forecast_with_ffnn_monitored(
    time_series, n_lags=14, hidden_units_options=[32, 64, 128], epochs=50, batch_size=16,
    retrain_threshold=1.5, retrain_numb_flags=3, seed=0, future_steps=50, plot_results=True
):
    # Set seed for reproducibility
    np.random.seed(seed)
    tf.random.set_seed(seed)
    random.seed(seed)

    # Ensure the time series is ordered and has no missing values
    time_series = time_series.dropna()
    time_series = time_series.sort_index()

    # Split the time series into training, validation, and test sets
    train_size = int(len(time_series) * 0.7)
    val_size = int(len(time_series) * 0.2)

    train = time_series.iloc[:train_size]
    validation = time_series.iloc[train_size:train_size + val_size]
    test = time_series.iloc[train_size + val_size:]

    print(f'Training data length: {len(train)}')

    # Scale the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    train_scaled = scaler.fit_transform(train.values.reshape(-1, 1))
    validation_scaled = scaler.transform(validation.values.reshape(-1, 1))
    test_scaled = scaler.transform(test.values.reshape(-1, 1))
    train_val_scaled = np.vstack([train_scaled, validation_scaled])

    # Prepare the data (sliding window)
    def prepare_data(series, n_lags):
        series = np.array(series)
        X = np.lib.stride_tricks.sliding_window_view(series, window_shape=n_lags)[:-1]
        y = series[n_lags:]
        return X, y

    X_train_val, y_train_val = prepare_data(train_val_scaled.flatten(), n_lags)
    X_test, y_test = prepare_data(test_scaled.flatten(), n_lags)

    # Split train and validation
    split_idx = len(train)
    X_train, y_train = X_train_val[:split_idx - n_lags], y_train_val[:split_idx - n_lags]
    X_val, y_val = X_train_val[split_idx - n_lags:], y_train_val[split_idx - n_lags:]

    # Reshape data
    X_train = X_train.reshape(X_train.shape[0], n_lags)
    X_val = X_val.reshape(X_val.shape[0], n_lags)
    X_test = X_test.reshape(X_test.shape[0], n_lags)

    # Hyperparameter tuning
    best_rmse = float('inf')
    best_units = None
    for units in hidden_units_options:
        model = Sequential([
            Dense(units, activation='relu', input_dim=n_lags),
            Dense(units // 2, activation='relu'),
            Dense(1, activation = 'relu')
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)

        y_val_pred = model.predict(X_val).ravel()
        y_val_rescaled = scaler.inverse_transform(y_val.reshape(-1, 1)).ravel()
        y_val_pred_rescaled = scaler.inverse_transform(y_val_pred.reshape(-1, 1)).ravel()
        rmse = np.sqrt(mean_squared_error(y_val_rescaled, y_val_pred_rescaled))

        if rmse < best_rmse:
            best_rmse = rmse
            best_units = units

    # Final model training
    model = Sequential([
        Dense(best_units, activation='relu', input_dim=n_lags),
        Dense(best_units // 2, activation='relu'),
        Dense(1, activation = 'relu')
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train_val, y_train_val, epochs=epochs, batch_size=batch_size, verbose=0)

    # Initialize predictions
    predictions = []
    input_seq = X_test[0].reshape(1, -1)  # Starting input sequence
    rmse_list = []
    poor_performance_count = 0
    residuals_history = []

    for i in range(len(y_test) + future_steps):
        # Predict the next value
        pred = model.predict(input_seq).flatten()[0]
        predictions.append(pred)

        # Update input sequence: shift and add prediction
        input_seq = np.roll(input_seq, -1, axis=1)
        input_seq[0, -1] = pred

        if i <len(test.values):

          # Monitor performance
          actual_rescaled = test.values[i]
          pred_rescaled = scaler.inverse_transform(np.array([pred]).reshape(-1, 1)).flatten()[0]
          residual = abs(actual_rescaled-pred_rescaled)
          rmse = np.sqrt((actual_rescaled - pred_rescaled) ** 2)
          rmse_list.append(rmse)

          residuals_history.append(residual)

          # Check if retraining is needed
          if residual > retrain_threshold*np.mean(residuals_history):
              poor_performance_count += 1
          else:
              poor_performance_count = 0
          print(f'Poor perfromance count:{poor_performance_count}')
          print(f'Residual: {residual}')
          print(f'Mean residual: {np.mean(residuals_history)}')

          if poor_performance_count >= retrain_numb_flags:

              print(f"Retraining triggered at index {i}: Residual {residual}")

              ## Retrain model
              # Limit the data to the most recent observations for retraining
              start_idx = i
              retraining_data = np.concatenate([train_scaled[start_idx:].flatten(), test_scaled.flatten()[:i]])
              print(f'Retraining data length: {len(retraining_data)}')

              # Prepare retraining data
              X_train_retrain, y_train_retrain = prepare_data(retraining_data, n_lags)

              # Retrain the model with the new data
              model.fit(X_train_retrain, y_train_retrain, epochs=epochs, batch_size=batch_size, verbose=0)
              poor_performance_count = 0

    # Rescale predictions
    predictions_rescaled = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
    actual_rescaled = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

    # Plot results
    if plot_results:
      plt.figure(figsize=(10, 6))
      plt.plot(range(len(test)), test, label='Actual', color='blue')
      plt.plot(range(len(predictions_rescaled)), predictions_rescaled, label='Predictions', color='orange')
      
      # Calcola l'indice per l'inizio delle predizioni future
      future_start_idx = len(test)
      
      # Aggiungi la linea verticale
      plt.axvline(future_start_idx, color='green', linestyle='--', label='Future Predictions Start')
      
      # Aggiungi intervallo di incertezza
      plt.fill_between(
          range(len(predictions_rescaled)),
          np.array(predictions_rescaled) - 2 * np.std(rmse_list),
          np.array(predictions_rescaled) + 2 * np.std(rmse_list),
          color='orange', alpha=0.2, label='Uncertainty'
      )
      
      plt.legend()
      plt.show()
    return model, scaler


# Call the function with the provided time series
# model, scaler = forecast_with_ffnn_monitored(synthetic_series)
