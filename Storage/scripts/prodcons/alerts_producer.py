"""
This script is a Kafka producer that generates and sends alert messages to a specified Kafka topic.

The script allows the user to specify the number of messages to produce, the rate of production,
a fixed machine ID (or random if not specified), and a seed for the random generator.

Command Line Arguments:
    -a, --amount: Amount of messages to produce (default: 5)
    -r, --rate: Rate of production in milliseconds (default: 1000)
    -m, --machine: Machine ID (uses random ID if not specified)
    -S, --seed: Seed for the random generator (default: 0)

Example Usage:
    python alerts_producer.py -a 10 -r 500 -m 1 -S 42

Dependencies:
    - confluent_kafka
    - argparse
    - random
    - time
    - json
"""

import random
import argparse
from confluent_kafka import Producer
from time import sleep
import json


HOST = "localhost"
PORT = "9092"
TOPIC = "alerts"


def delivery_callback(err, msg):
    """
    Callback function to handle the delivery report of a message.

    This function is called once for each message produced to indicate whether the message
    was successfully delivered or if there was an error.

    Args:
        err (KafkaError or None): The error that occurred during message delivery, or None if the message was delivered successfully.
        msg (Message): The message that was produced.

    Returns:
        None
    """
    if err:
        print("ERROR: Message failed delivery: {}".format(err))
    else:
        print(
            "Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(),
                key=msg.key().decode("utf-8"),
                value=msg.value().decode("utf-8"),
            )
        )


if __name__ == "__main__":

    # parse command line arguments
    parser = argparse.ArgumentParser(description="Kafka Producer")
    parser.add_argument(
        "-a", "--amount", type=int, help="Amount of messages to produce", default=5
    )
    parser.add_argument(
        "-r", "--rate", type=int, help="Rate of Production (ms)", default=1000
    )
    parser.add_argument(
        "-m",
        "--machine",
        type=int,
        help="Machine ID (Does not use random ID)",
        default=None,
    )
    parser.add_argument(
        "-S", "--seed", type=int, help="Seed for Random Generator", default=0
    )

    args = parser.parse_args()

    # seed random generator
    random.seed(args.seed)

    # create configuration
    config = {
        # User-specific properties that you must set
        "bootstrap.servers": f"{HOST}:{PORT}",
        # Fixed properties
        "acks": "all",
    }

    producer = Producer(config)

    for i in range(args.amount):
        # create random alert
        alert = {
            "machine": random.randint(1, 100) if args.machine is None else args.machine,
            "severity": random.randint(1, 3),
            "description": f"Alert {random.randint(1, 100)}",
            "KPI": f"KPI {random.randint(1, 100)}",
        }

        # produce alert
        producer = Producer(config)
        producer.produce(
            TOPIC,
            key=str(alert["machine"]).encode("utf-8"),
            value=json.dumps(alert),
            callback=delivery_callback,
        )

        sleep(args.rate / 1000)
        producer.poll(args.rate)
        producer.flush()
