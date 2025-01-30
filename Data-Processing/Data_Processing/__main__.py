"""
This script is designed to retrieve, process, and handle both historical and real-time data for a specific application. 
It performs the following key tasks:
1. Loads the timestamp of the last processed data to resume from the correct point.
2. Retrieves and processes historical data until a sufficient dataset is available for model training.
3. Continuously monitors and processes new incoming data in real-time at regular intervals.
4. Updates the last processed timestamp to ensure continuity and prevent redundant processing.
"""

import json
import time
from datetime import datetime, timedelta
from Data_Processing.streaming_main import *
from Data_Processing.historical_main import *
from Data_Processing.api_interaction import *

# DEFINITION OF GLOBAL CONSTANTS
min_sample_models = 120  # Minimum number of samples required to initiate model training
sleep_interval = 3600  # Time (in seconds) between checks for new data
output_dir = "metadata_storage" # folder for timestamp ecc...

file_path = '/usr/src/app/metadata_storage/last_timestamp.json'

def load_last_timestamp():
    """
    Load the timestamp of the last processed data from a local JSON file.

    Returns:
        datetime or None: The last processed timestamp if the file exists, otherwise None.
    """
    
    # Check if the file exists and is not empty
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                return data.get("last_timestamp", None)
            except json.JSONDecodeError:
                print(f"Error decoding the JSON file: {file_path}")
                return None
    else:
        print(f"The file {file_path} is empty or does not exist.")
        return None

def save_timestamp(timestamp):
    """
    Save the current timestamp to a JSON file.

    Args:
        timestamp (datetime): The timestamp to save.
    """

    if isinstance(timestamp, str):
        timestamp = datetime.datetime.fromisoformat(timestamp)

    os.makedirs(output_dir, exist_ok = True)
    with open(file_path, "w") as f:
        json.dump({"last_timestamp": timestamp.isoformat()}, f)

    #print('last_timestamp saved! ', timestamp.isoformat())

def retrieve_and_process_data():
    """
    Retrieve and process historical data until the minimum required samples are collected.
    Also, save the most recent timestamp to a local JSON file.
    """
    # Uncomment if you want to run the historical processing from the current timestamp
    #last_timestamp = load_last_timestamp()  # Load the last processed timestamp
    # otherwise, historical processing is done on the whole dataset 
    last_timestamp = None

    # Convert to date if string
    if last_timestamp:
        if isinstance(last_timestamp, str):
            last_timestamp = datetime.datetime.fromisoformat(last_timestamp)
        start_time = last_timestamp + timedelta(days=1) if last_timestamp else None
    else:
        start_time = None

    enough_data = False
    while not enough_data:
        print("Waiting for sufficient data...")
        # Retrieve historical data starting from the last processed timestamp
        historical_data = retrieve_data(start_time=start_time)
        if len(historical_data) > 0 and len(historical_data["timestamp"].unique()) > min_sample_models:
            enough_data = True
        else:
            time.sleep(60)  # Wait before retrying if not enough data is retrieved

    print("Starting historical data processing...")
    #testing_historical_data = historical_data[(historical_data['machineID'] == 5) & (historical_data['aggr_type'] == 'sum') & (historical_data['kpi'] == 'power')]
    #historical_processing(testing_historical_data)  # Process the historical data
    historical_processing(historical_data)  # Process the historical data
    print("Historical data processing completed.")

    # Save the timestamp of the most recent data
    most_recent_timestamp = historical_data["timestamp"].max()
    save_timestamp(most_recent_timestamp)

def process_new_data():
    """
    Check for and process new incoming data in streaming mode.
    Save the most recent timestamp after successful processing.
    """
    
    last_timestamp = load_last_timestamp()  # Load the last processed timestamp
    print('last_timestamp loaded: ', last_timestamp)

    new_data = retrieve_data(start_time=last_timestamp) #+ timedelta(days=1))  # Retrieve new data

    #testing_new_data = new_data[(new_data['machineID'] == 5) & (new_data['aggr_type'] == 'sum') & (new_data['kpi'] == 'power') & (new_data['timestamp'] == new_data['timestamp'].max())]
    #new_data = testing_new_data

    if new_data.empty:
        print("No new data retrieved.")
    else:
        print("Starting new data processing...")
        # cycling on the new_data: 
        grouped = new_data.groupby(['machineID', 'kpi', 'aggr_type'])
        for (machineID, kpi, aggr_type), group in grouped:
            group = group.sort_values(by='timestamp')
            for _, row in group.iterrows():
                streaming_processing(row)
            #streaming_processing(new_data)  # Process the new data in streaming mode

            print("New data processing done.")
            # Save the timestamp of the most recent data
            most_recent_timestamp = new_data["timestamp"].max()
            last_timestamp = most_recent_timestamp
            save_timestamp(most_recent_timestamp)

        print('New data processing finished.')

if __name__ == '__main__':
    """
    Main entry point of the application. 
    The script first retrieves and processes historical data and then enters a loop 
    to continuously check for new data at regular intervals.
    """
    print("Application is starting...")  # Log the start of the application

    # Initial processing of historical data
    retrieve_and_process_data()

    # Continuous monitoring and processing of new data
    while True:
        process_new_data()  # Check and process new data
        time.sleep(sleep_interval)  # Wait for the defined interval before the next check
