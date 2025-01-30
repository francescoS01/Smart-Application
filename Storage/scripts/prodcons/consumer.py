"""
This script is a generic Kafka consumer that connects to a Kafka broker,
subscribes to a specified topic, and continuously polls for new messages.
When a new message is received, it parses the JSON content and prints
the machine information and measurement data to the console.

Usage:
    python consumer.py

Configuration:
    HOST: The hostname of the Kafka broker.
    PORT: The port number of the Kafka broker.
    TOPIC: The Kafka topic to subscribe to.

Kafka Consumer Configuration:
    bootstrap.servers: A list of host/port pairs to use for establishing the initial connection to the Kafka cluster.
    group.id: A unique string that identifies the consumer group this consumer belongs to.
    auto.offset.reset: What to do when there is no initial offset in Kafka or if the current offset does not exist any more on the server.

Dependencies:
    confluent_kafka: Python client for Apache Kafka.
    json: Library to parse JSON formatted messages.

Example:
    To run the consumer, execute the following command:
        $ python consumer.py

    The consumer will connect to the Kafka broker at localhost:9092, subscribe to the 'measurements' topic, and print the machine information and measurement data for each message received.
"""

from confluent_kafka import Consumer
import json

HOST = "localhost"
PORT = 9092
TOPIC = "measurements"


if __name__ == "__main__":

    config = {
        # User-specific properties that you must set
        "bootstrap.servers": f"{HOST}:{PORT}",
        # Fixed properties
        "group.id": "kafka-python-getting-started",
        "auto.offset.reset": "earliest",
    }

    # Create Consumer instance
    consumer = Consumer(config)

    # Subscribe to topic
    consumer.subscribe([TOPIC])

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                print("Waiting...")
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                data = json.loads(msg.value())
                machine_info = data["machine"]
                measurement = data["measurement"]
                print(f"Machine Info: {machine_info}")
                print(f"Measurement: {measurement}")
                print(f"Timestamp: {msg.timestamp()}")

    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
