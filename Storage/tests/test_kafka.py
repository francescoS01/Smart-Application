"""
This module contains unit tests for the Kafka integration in the Storage package.
It tests the functionality of producing and consuming messages using Kafka.
"""

import pytest
import Storage.kafka as kafka
from confluent_kafka import KafkaException
import json

# Initialize Kafka configurations
kafka.init_configs("localhost", "9092")

def test_get_producer():
    producer = kafka.get_producer()
    assert producer is not None


def test_get_consumer():
    consumer = kafka.get_consumer("test_group", ["measurements"])
    assert consumer is not None


def test_get_consumer_empty_group():
    with pytest.raises(KafkaException):
        kafka.get_consumer("", ["measurements"])


def test_get_consumer_empty_topics():
    with pytest.raises(KafkaException):
        kafka.get_consumer("test_group", [])


def test_get_consumer_invalid_group():
    with pytest.raises(KafkaException):
        consumer = kafka.get_consumer(None, ["measurements"])


def test_get_consumer_invalid_topics():
    with pytest.raises(TypeError):
        consumer = kafka.get_consumer("test_group", None)


def test_put_message():
    producer = kafka.get_producer()
    kafka.put_message(producer, "measurements", "key", "value")


def test_put_message_invalid_topic():
    producer = kafka.get_producer()
    with pytest.raises(TypeError):
        kafka.put_message(producer, None, "key", "value")


def test_put_message_json():
    producer = kafka.get_producer()
    data = {"key": "value"}
    kafka.put_message(producer, "measurements", "key", json.dumps(data))
