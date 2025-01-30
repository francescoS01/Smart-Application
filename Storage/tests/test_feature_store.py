import pytest
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from feast import FeatureStore
import sys

sys.path.append("..")

from Storage.feature_store_utils import (
    new_engine,
    start_store,
    insert_data_to_sql,
    get_data_from_sql,
    delete_data_from_sql,
    get_filtered_online_features,
    insert_data_to_redis,
    insert_new_data,
)


@pytest.fixture(scope="module")
def engine():
    return new_engine()


@pytest.fixture(scope="module")
def store(repo_path="../postgres_store/feature_repo"):
    return start_store(repo_path)


@pytest.fixture(scope="module")
def sample_data():
    data = {
        "timestamp": [
            datetime.now(),
            datetime(2024, 11, 21, 8, 12, 10),
            datetime(2024, 11, 17, 16, 40, 26),
            datetime(2024, 11, 21, 8, 12, 10),
        ],
        "machineid": ["1", "2", "3", "1"],
        "kpi": ["x_acceleration", "y_acceleration", "z_acceleration", "x_acceleration"],
        "aggregation_type": ["avg", "avg", "avg", "avg"],
        "value": [1.0, 2.0, 3.0, 4.0],
        "imputation": [False, False, True, False],
        "anomaly": [False, False, True, False],
        "trend_drift": [0.1, 0.2, 0.3, 0.4],
        "next_days_predictions": [
            [
                75.5,
                75.6,
                75.7,
                75.8,
                75.9,
                76.0,
                76.1,
                76.2,
                76.3,
                76.4,
                76.5,
                76.6,
                76.7,
                76.8,
                76.9,
                77.0,
                77.1,
                77.2,
                77.3,
                77.4,
                77.5,
            ],
            [
                75.5,
                75.6,
                75.7,
                75.8,
                75.9,
                76.0,
                76.1,
                76.2,
                76.3,
                76.4,
                76.5,
                76.6,
                76.7,
                76.8,
                76.9,
                77.0,
                77.1,
                77.2,
                77.3,
                77.4,
                77.5,
            ],
            [
                75.5,
                75.6,
                75.7,
                75.8,
                75.9,
                76.0,
                76.1,
                76.2,
                76.3,
                76.4,
                76.5,
                76.6,
                76.7,
                76.8,
                76.9,
                77.0,
                77.1,
                77.2,
                77.3,
                77.4,
                77.5,
            ],
            [
                75.5,
                75.6,
                75.7,
                75.8,
                75.9,
                76.0,
                76.1,
                76.2,
                76.3,
                76.4,
                76.5,
                76.6,
                76.7,
                76.8,
                76.9,
                77.0,
                77.1,
                77.2,
                77.3,
                77.4,
                77.5,
            ],
        ],
        "confidence_interval_lower": [
            [
                75.4,
                75.5,
                75.6,
                75.7,
                75.8,
                75.9,
                76.0,
                76.1,
                76.2,
                76.3,
                76.4,
                76.5,
                76.6,
                76.7,
                76.8,
                76.9,
                77.0,
                77.1,
                77.2,
                77.3,
                77.4,
            ],
            [
                75.4,
                75.5,
                75.6,
                75.7,
                75.8,
                75.9,
                76.0,
                76.1,
                76.2,
                76.3,
                76.4,
                76.5,
                76.6,
                76.7,
                76.8,
                76.9,
                77.0,
                77.1,
                77.2,
                77.3,
                77.4,
            ],
            [
                75.4,
                75.5,
                75.6,
                75.7,
                75.8,
                75.9,
                76.0,
                76.1,
                76.2,
                76.3,
                76.4,
                76.5,
                76.6,
                76.7,
                76.8,
                76.9,
                77.0,
                77.1,
                77.2,
                77.3,
                77.4,
            ],
            [
                75.4,
                75.5,
                75.6,
                75.7,
                75.8,
                75.9,
                76.0,
                76.1,
                76.2,
                76.3,
                76.4,
                76.5,
                76.6,
                76.7,
                76.8,
                76.9,
                77.0,
                77.1,
                77.2,
                77.3,
                77.4,
            ],
        ],
        "confidence_interval_upper": [
            [
                75.6,
                75.7,
                75.8,
                75.9,
                76.0,
                76.1,
                76.2,
                76.3,
                76.4,
                76.5,
                76.6,
                76.7,
                76.8,
                76.9,
                77.0,
                77.1,
                77.2,
                77.3,
                77.4,
                77.5,
                77.6,
            ],
            [
                75.6,
                75.7,
                75.8,
                75.9,
                76.0,
                76.1,
                76.2,
                76.3,
                76.4,
                76.5,
                76.6,
                76.7,
                76.8,
                76.9,
                77.0,
                77.1,
                77.2,
                77.3,
                77.4,
                77.5,
                77.6,
            ],
            [
                75.6,
                75.7,
                75.8,
                75.9,
                76.0,
                76.1,
                76.2,
                76.3,
                76.4,
                76.5,
                76.6,
                76.7,
                76.8,
                76.9,
                77.0,
                77.1,
                77.2,
                77.3,
                77.4,
                77.5,
                77.6,
            ],
            [
                75.6,
                75.7,
                75.8,
                75.9,
                76.0,
                76.1,
                76.2,
                76.3,
                76.4,
                76.5,
                76.6,
                76.7,
                76.8,
                76.9,
                77.0,
                77.1,
                77.2,
                77.3,
                77.4,
                77.5,
                77.6,
            ],
        ],
    }
    return pd.DataFrame(data)


def test_insert_data_to_sql(engine, sample_data):
    insert_data_to_sql(sample_data, "historical_store", engine)
    result = get_data_from_sql("historical_store", engine)
    assert not result.empty


def test_get_data_from_sql(engine):
    result = get_data_from_sql(
        "historical_store", engine, attributes=["machineid", "kpi"]
    )
    assert not result.empty
    assert "machineid" in result.columns
    assert "kpi" in result.columns


def test_delete_data_from_sql(engine):
    delete_data_from_sql("historical_store", engine, conditions={"MachineID": 1})
    result = get_data_from_sql("historical_store", engine, conditions={"MachineID": 1})
    assert result.empty


def test_get_filtered_online_features(store):
    conditions = {"machineid": [1], "kpi": ["temperature"], "aggregation_type": ["avg"]}
    attributes = ["value"]
    result = get_filtered_online_features(
        store, "historical_store", attributes, conditions
    )
    assert not result.empty


def test_insert_data_to_redis(store, sample_data):
    insert_data_to_redis(sample_data, store, "historical_store")
    # Assuming there's a way to verify data in Redis, add assertions here


def test_insert_new_data(engine, store, sample_data):
    insert_new_data(sample_data, "historical_store", engine, store)
    result_sql = get_data_from_sql("historical_store", engine)
    assert not result_sql.empty
    # Assuming there's a way to verify data in Redis, add assertions here
