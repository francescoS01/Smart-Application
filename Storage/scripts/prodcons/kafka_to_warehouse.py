"""
This script consumes messages from Kafka topics and stores the data into a PostgreSQL database.
It handles two types of messages: alerts and measurements.

Configuration:
- HOST: Kafka broker host
- PORT: Kafka broker port
- TOPICS: List of Kafka topics to subscribe to

Dependencies:
- confluent_kafka: For consuming messages from Kafka
- psycopg2: For connecting to PostgreSQL database
- json: For parsing JSON messages
- datetime: For handling timestamps

Functions:
- get_consumer: Creates and returns a Kafka consumer
- get_message: Polls and returns a message from Kafka
- put_alert_data: Inserts alert data into the database
- put_machine_data: Inserts machine data into the database
- put_measurement: Inserts measurement data into the database
- get_machine_data_by_name: Retrieves machine data by name from the database

Usage:
Run the script to start consuming messages from Kafka and storing them into the PostgreSQL database.
"""

from confluent_kafka import (
    Consumer,
    TIMESTAMP_NOT_AVAILABLE,
    TIMESTAMP_CREATE_TIME,
    TIMESTAMP_LOG_APPEND_TIME,
)
import json
import psycopg2
from datetime import datetime
from Storage.kafka import get_consumer, get_message, init_configs
from Storage.warehouse import (
    put_alert_data,
    put_measurement,
    get_machine_data_by_name,
    get_connection,
)
import argparse
import os
from dotenv import load_dotenv

load_dotenv()
TOPICS = ["measurements", "alerts"]
# KAFKA_HOST = os.environ["KAFKA_HOST"] if "KAFKA_HOST" in os.environ else "localhost"
# KAFKA_PORT = os.environ["KAFKA_PORT"] if "KAFKA_PORT" in os.environ else "9092"
# POSTGRES_HOST = (
#     os.environ["POSTGRES_HOST"] if "POSTGRES_HOST" in os.environ else "localhost"
# )


if __name__ == "__main__":

    # parse command line arguments
    parser = argparse.ArgumentParser(description="Kafka to Warehouse")
    parser.add_argument("-l", "--local", help="Use local Kafka broker", default=False)
    args = parser.parse_args()
    # Create Consumer instance
    # print(KAFKA_HOST, KAFKA_PORT)
    # init_configs(KAFKA_HOST, KAFKA_PORT)
    kafka_host = "localhost" if args.local else os.getenv("KAFKA_HOST", "localhost")
    kafka_port = "9092" if args.local else os.getenv("KAFKA_PORT", "9092")
    postgres_host = (
        "localhost" if args.local else os.getenv("POSTGRES_HOST", "localhost")
    )

    init_configs(kafka_host, kafka_port)
    print("Starting Kafka to Warehouse")
    consumer = get_consumer("kafka-to-warehouse", TOPICS)
    print("Connected to Kafka")
    print("Connecting to PostgreSQL")
    conn = get_connection(host=postgres_host)
    conn.autocommit = True
    print("Connected to PostgreSQL")

    # Poll for new messages from Kafka and print them.
    print("Polling for messages...")
    try:
        while True:
            msg = get_message(consumer)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                # print("Waiting...")
                continue
            elif msg.error():
                print(f"ERROR: {msg.error()}")
            else:  # message arrived

                # check if alert or measurement
                data = json.loads(msg.value())
                if "severity" in data.keys():
                    alert = data
                    # Inserting data into table
                    (time_type, timestamp) = msg.timestamp()
                    if time_type == TIMESTAMP_NOT_AVAILABLE:
                        timestamp = datetime.now()
                    else:
                        timestamp = datetime.fromtimestamp(timestamp / 1000)

                    print(
                        f"Alert: {alert['machine']}, {alert['severity']}, {alert['KPI']}"
                    )
                    try:
                        put_alert_data(
                            alert["machine"],
                            alert["KPI"],
                            alert["description"],
                            alert["severity"],
                            timestamp,
                        )
                        conn.commit()
                    except Exception as e:
                        print(f"Error inserting alert data: {e}")
                        continue
                else:
                    machine_id = data["machine"]
                    measurement = data["measurement"]

                    (time_type, timestamp) = msg.timestamp()

                    if time_type == TIMESTAMP_NOT_AVAILABLE:
                        timestamp = datetime.now()
                    else:
                        timestamp = datetime.fromtimestamp(timestamp / 1000)

                    try:
                        put_measurement(machine_id, timestamp, measurement)
                        conn.commit()
                    except Exception as e:
                        print(f"Error inserting measurement data: {e}")
                        continue
                    print(f"Machine: {machine_id}, Measurement: {measurement}")

    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
