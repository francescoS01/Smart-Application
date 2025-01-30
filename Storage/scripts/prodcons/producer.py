"""
Kafka Producer Script

This script generates random sensor measurements and sends them to a Kafka topic.

Usage:
    python producer.py [options]

Options:
    -m, --machine    Machine Number (default: 0)
    -n, --name       Machine Name (default: "A")
    -l, --line       Line Number (default: 0)
    -s, --site       Site Number (default: "H")
    -t, --type       Machine Type (default: "X")
    -S, --seed       Seed for Random Generator (default: 0)
    -r, --rate       Rate of Production in milliseconds (default: 1000)
    -a, --amount     Amount of messages to produce (default: 5)

Description:
    This script initializes a Kafka producer and generates random sensor measurements
    based on the provided command line arguments. The generated measurements are then
    sent to the specified Kafka topic at the specified rate.

Example:
    python producer.py -m 1 -n "Machine1" -l 2 -s "SiteA" -t "TypeB" -S 42 -r 500 -a 10
"""

import random
import argparse
import json
from time import sleep
from Storage.message_generator import Measurement, SensorMeasurement
from Storage.kafka import get_producer, put_message, init_configs

TOPIC = "measurements"


if __name__ == "__main__":

    # parse command line arguments
    parser = argparse.ArgumentParser(description="Kafka Producer")
    parser.add_argument("-m", "--machine", type=int, help="Machine Number", default=0)
    parser.add_argument("-n", "--name", type=str, help="Machine Name", default="A")
    parser.add_argument("-l", "--line", type=int, help="Line Number", default=0)
    parser.add_argument("-s", "--site", type=str, help="Site Number", default="H")
    parser.add_argument("-t", "--type", type=str, help="Machine Type", default="X")
    parser.add_argument(
        "-S", "--seed", type=int, help="Seed for Random Generator", default=0
    )
    parser.add_argument(
        "-r", "--rate", type=int, help="Rate of Production (ms)", default=1000
    )
    parser.add_argument(
        "-a", "--amount", type=int, help="Amount of messages to produce", default=5
    )
    args = parser.parse_args()

    # seed random generator
    random.seed(args.seed)
    machine_info = {
        "name": args.name,
        "machine": args.machine,
        "line": args.line,
        "factory": args.site,
        "machine_type": args.type,
    }

    # Create Producer instance
    init_configs('localhost', '9092')
    producer = get_producer()

    # Create a SensorMeasurement instance
    measurements = [m for m in Measurement]
    sensor = SensorMeasurement(measurements)

    for i in range(args.amount):
        # Create a message
        message = sensor.generate_random_measurement()
        # as message uses enum, it needs to be converted to string
        message = {m.value: message[m] for m in message}
        data = {"machine": args.name, "measurement": message}
        print(f"Producing message: {data}")

        put_message(
            producer,
            TOPIC,
            key=str(args.machine),
            value=json.dumps(data),
            rate=args.rate / 1000,
        )

        sleep(args.rate / 1000)
