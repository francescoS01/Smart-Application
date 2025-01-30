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
from streaming_main import *  # Contains functions for processing new data in streaming mode
from historical_main import *  # Contains functions for processing historical data
from api_interaction import *  # Contains functions for retrieving data from an external API

# DEFINITION OF GLOBAL CONSTANTS
min_sample_models = 120  # Minimum number of samples required to initiate model training
sleep_interval = 3600  # Time (in seconds) between checks for new data

def load_last_timestamp():
    """
    Load the timestamp of the last processed data from a local JSON file.

    Returns:
        datetime or None: The last processed timestamp if the file exists, otherwise None.
    """
    try:
        with open("last_timestamp.json", "r") as f:
            last_timestamp = json.load(f)
            return datetime.fromisoformat(last_timestamp.get("last_timestamp"))
    except FileNotFoundError:
        # Return None if the file does not exist
        return None

def save_timestamp(timestamp):
    """
    Save the current timestamp to a JSON file.

    Args:
        timestamp (datetime): The timestamp to save.
    """
    with open("last_timestamp.json", "w") as f:
        json.dump({"last_timestamp": timestamp.isoformat()}, f)

def retrieve_and_process_data():
    """
    Retrieve and process historical data until the minimum required samples are collected.
    Also, save the most recent timestamp to a local JSON file.
    """
    last_timestamp = load_last_timestamp()  # Load the last processed timestamp
    start_time = last_timestamp + timedelta(days=1) if last_timestamp else None
    data_length = 0

    while data_length < min_sample_models:
        print("Waiting for sufficient data...")
        # Retrieve historical data starting from the last processed timestamp
        historical_data = retrieve_data(start_time=start_time)
        data_length = len(historical_data["time_stamp"].unique())  # Count unique timestamps
        time.sleep(60)  # Wait before retrying if not enough data is retrieved

    print("Starting historical data processing...")
    historical_processing(historical_data)  # Process the historical data
    print("Historical data processing completed.")

    # Save the timestamp of the most recent data
    most_recent_timestamp = historical_data["time_stamp"].max()
    save_timestamp(most_recent_timestamp)

def process_new_data():
    """
    Check for and process new incoming data in streaming mode.
    Save the most recent timestamp after successful processing.
    """
    last_timestamp = load_last_timestamp()  # Load the last processed timestamp
    new_data = retrieve_data(start_time=last_timestamp + timedelta(days=1))  # Retrieve new data

    if new_data.empty:
        print("No new data retrieved.")
    else:
        print("Starting new data processing...")
        streaming_processing(new_data)  # Process the new data in streaming mode
        print("New data processing completed.")

        # Save the timestamp of the most recent data
        most_recent_timestamp = new_data["time_stamp"].max()
        save_timestamp(most_recent_timestamp)

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
