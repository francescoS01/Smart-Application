"""
Kafka Producer Script

This script simulates a Kafka producer that generates random sensor measurements
for a specified machine and sends them to a Kafka topic. The script allows for
customization of the machine details, random seed, production rate, amount of messages,
and batch size through command line arguments.

Command Line Arguments:
    -n, --name: Machine Name (default: "machine1")
    -s, --seed: Seed for Random Generator (default: 0)
    -r, --rate: Rate of Production in milliseconds (default: 1000)
    -a, --amount: Amount of messages to produce (default: 5)
    -t, --type: Machine Type (default: "X")
    -l, --line: Line Number (default: 0)
    -f, --factory: Factory Name (default: "H")
    -b, --batch: Batch Size (default: 10)

The script initializes a Kafka producer, generates random sensor measurements,
computes KPIs (mean, max, min, sum) for each measurement, and sends the data
to the specified Kafka topic.
"""

import random
import argparse
import json
from time import sleep
from Storage.message_generator import Measurement, SensorMeasurement
from Storage.kafka import get_producer, put_message, init_configs
from Storage.warehouse import put_machine_data, get_machine_data_by_name
import numpy as np

TOPIC = "measurements"

if __name__ == "__main__":

    print("Hello World")
    # parse command line arguments
    parser = argparse.ArgumentParser(description="Kafka Producer")
    parser.add_argument(
        "-n", "--name", type=str, help="Machine Name", default="machine1"
    )
    parser.add_argument(
        "-s", "--seed", type=int, help="Seed for Random Generator", default=0
    )
    parser.add_argument(
        "-r", "--rate", type=int, help="Rate of Production (ms)", default=1000
    )
    parser.add_argument(
        "-a", "--amount", type=int, help="Amount of messages to produce", default=5
    )
    parser.add_argument("-t", "--type", type=str, help="Machine Type", default="X")
    parser.add_argument("-l", "--line", type=int, help="Line Number", default=0)
    parser.add_argument("-f", "--factory", type=str, help="Factory Name", default="H")
    parser.add_argument("-b", "--batch", type=int, help="Batch Size", default=10)

    args = parser.parse_args()

    # initialize random generator
    random.seed(args.seed)
    try:
        # TODO: replace with api call to insert machine data
        id = put_machine_data(args.name, args.type, args.line, args.factory)
    except Exception as e:
        # TODO: replace with api call to get machine data by name
        id = get_machine_data_by_name(args.name)[0][0]

    print(f"Machine ID: {id}")
    # create producer instance
    # TODO: replace if executed in container
    init_configs("localhost", "9092")
    producer = get_producer()

    # measurements excluded from generation
    # TODO: replace here if decide to create new measurements
    exclude = [
        Measurement.ACCELERATION_X,
        Measurement.ACCELERATION_Y,
        Measurement.ACCELERATION_Z,
        Measurement.TEMPERATURE,
    ]
    # create a SensorMeasurement instance
    measurements = [m for m in Measurement if m not in exclude]
    sensor = SensorMeasurement(measurements)

    for i in range(args.amount):
        messages = [sensor.generate_random_measurement() for _ in range(args.batch)]

        # messages is a list of dictionaries, convert to dictionary of lists
        data = {m.value: [msg[m] for msg in messages] for m in messages[0]}

        # now compute mean, max, min and sum for each list.
        # the final result is a dictionary, where the keys are the kpis, and the values are an object of the form:
        # { "mean": float, "max": float, "min": float, "sum": float }

        kpis = {
            m: {
                "mean": np.mean(data[m]),
                "max": np.max(data[m]),
                "min": np.min(data[m]),
                "sum": np.sum(data[m]),
            }
            for m in data
        }
        print("Producing message:")
        print(json.dumps(kpis, indent=4))

        data = {"machine": id, "measurement": kpis}

        # TODO replace with api call to send message
        put_message(
            producer,
            TOPIC,
            key=str(
                id
            ),  # key not necessary as we do not have a cluster, but still useful to do it
            value=json.dumps(data),  # the data you need to send
            rate=args.rate / 1000,  # rate of production
        )

        sleep(args.rate / 1000)
