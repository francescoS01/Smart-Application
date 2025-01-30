"""
This script is a Kafka consumer that listens to the 'alerts' topic for incoming messages.

It uses the Confluent Kafka Python client to connect to a Kafka broker running on localhost at port 9092.
The consumer is configured with a group ID and an offset reset policy.

Steps:
1. Configuration: Sets up the Kafka consumer configuration, including the bootstrap servers, group ID, and offset reset policy.
2. Consumer Instance: Creates a Kafka consumer instance with the specified configuration.
3. Subscription: Subscribes the consumer to the 'alerts' topic.
4. Polling Loop: Enters an infinite loop where it polls for new messages from Kafka:
   - If no message is received, it prints "Waiting...".
   - If an error occurs, it prints the error.
   - If a message is received, it parses the message value as JSON and prints the alert.
5. Graceful Shutdown: Handles keyboard interrupts to allow for a graceful shutdown, ensuring the consumer leaves the group and commits final offsets before closing.
"""

from confluent_kafka import Consumer
import json

HOST = "localhost"
PORT = 9092
TOPIC = "alerts"

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
                # Extract the (optional) key and value, and print.
                alert = json.loads(msg.value())
                print(f"Alert: {alert}")

    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
