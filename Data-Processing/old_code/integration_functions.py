# functions for integrating with other groups 
# send warning
def send_warning(label, description):
  if label == 'Invalid data':
    print(description) ## ask which group!
  elif label == 'Ex_inconsistency':
    print(description) ## ask which group!
  elif label == 's_missing_data':
    print(description) ## ask which group!
  elif label == 'Positive_trend_drift':
    print(description) ## ask which group!
  elif label == 'Negative_trend_drift':
    print(description) ## ask which group!
  elif label == 'Anomaly_streaming':
    print(description) ## ask which group!
  else:
    print(description) ## ask which group!
  return None

# Send preprocessed data and extracted features
def send_preprocessed_data(time_series):
  # load(current_data, database_warehouse)
  return None

# save values in historical feature store
def save_value(value):
  return None
