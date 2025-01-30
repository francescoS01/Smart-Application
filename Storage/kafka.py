"""
This module provides functions to interact with a Kafka cluster.

It includes functions to initialize Kafka configurations, produce messages to Kafka topics,
and consume messages from Kafka topics. The module uses the confluent_kafka library to
interface with Kafka.

Functions:
- delivery_callback: Callback function to handle the delivery report of a message.
- init_configs: Initializes the Kafka host and port configurations.
- get_producer: Creates and returns a Kafka producer with the specified configuration.
- put_message: Sends a message to a Kafka topic using the provided producer.
- get_consumer: Creates and returns a Kafka consumer configured with the specified group ID and subscribed to the given list of topics.
- get_message: Polls the Kafka consumer for a message.
"""

from confluent_kafka import Producer, Consumer
import os
from dotenv import load_dotenv

load_dotenv()


HOST = os.environ["KAFKA_HOST"] if "KAFKA_HOST" in os.environ else "localhost"
PORT = os.environ["KAFKA_PORT"] if "KAFKA_PORT" in os.environ else "9092"


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
        print(f"Message delivered to {msg.topic()} ")


def init_configs(host, port):
    """
    Initializes the Kafka host and port configurations.

    Args:
        host (str): The Kafka host name.
        port (str): The Kafka port number.

    Returns:
        None
    """
    global HOST
    global PORT
    HOST = host
    PORT = port


def get_producer():
    """
    Creates and returns a Kafka producer with the specified configuration.

    The configuration includes the bootstrap servers and acknowledgment settings.

    Returns:
        Producer: A Kafka producer instance configured with the specified settings.
    """
    config = {
        "bootstrap.servers": f"{HOST}:{PORT}",
        "acks": "all",
    }
    return Producer(config)


def put_message(producer, topic, key, value, rate=1.0):
    """
    Sends a message to a Kafka topic using the provided producer.

    Args:
        producer (confluent_kafka.Producer): The Kafka producer instance.
        topic (str): The name of the Kafka topic to which the message will be sent.
        key (str): The key associated with the message.
        value (str): The value of the message to be sent.
        rate (float, optional): The rate at which to poll the producer for message delivery status. Defaults to 1.0.

    Returns:
        None
    """
    producer.produce(
        topic,
        key=key,
        value=value,
        callback=delivery_callback,
    )

    # block until the message is sent (or timeout)
    producer.poll(rate)
    producer.flush()


def get_consumer(group_id, topics_list):
    """
    Creates and returns a Kafka consumer configured with the specified group ID and subscribed to the given list of topics.

    Args:
        group_id (str): The consumer group ID.
        topics_list (list of str): A list of topic names to subscribe to.

    Returns:
        Consumer: A Kafka consumer instance configured with the specified settings.

    Raises:
        TypeError: If any of the topics in topics_list is not a string.
    """
    for topic in topics_list:
        if not isinstance(topic, str):
            raise TypeError("Topics must be strings")
    config = {
        "bootstrap.servers": f"{HOST}:{PORT}",
        "group.id": group_id,
        "auto.offset.reset": "earliest",
    }
    consumer = Consumer(config)
    consumer.subscribe(topics_list)
    return consumer


def get_message(consumer):
    """
    Polls the Kafka consumer for a message.

    Args:
        consumer (KafkaConsumer): The Kafka consumer instance to poll messages from.

    Returns:
        msg (KafkaMessage): The message polled from the consumer, or None if no message is available within the timeout period.
    """
    msg = consumer.poll()
    return msg
