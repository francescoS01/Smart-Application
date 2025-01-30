"""
This module contains unit tests for the warehouse module in the Storage package.
The tests cover various functionalities such as retrieving measurements, 
inserting and deleting data, and handling edge cases.
"""

import Storage.warehouse as warehouse
import psycopg2
import pytest
from datetime import datetime


@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="password",
        port="5432",
    )
    conn.autocommit = True
    cursor = conn.cursor()
    yield cursor
    cursor.close()
    conn.close()


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown(db_connection):
    # Populate the database
    with open("Storage/scripts/postgres/populate.sql", "r") as f:
        db_connection.execute(f.read())
    yield
    # Depopulate the database
    with open("Storage/scripts/postgres/depopulate.sql", "r") as f:
        db_connection.execute(f.read())


def test_get_measurement_in_range(db_connection):
    result = warehouse.get_measurement_in_range(1, "temperature", datetime(2023, 10, 1, 8, 0, 0), datetime(2023, 10, 1, 10, 0, 0), 75, 80, statistic="mean")
    assert len(result) > 0
    for row in result:
        assert 75 <= float(row[2]["temperature"]["mean"]) <= 80


def test_get_measurement_in_range_no_results(db_connection):
    result = warehouse.get_measurement_in_range(1, "temperature", datetime(2023, 10, 1, 8, 0, 0), datetime(2023, 10, 1, 10, 0, 0), 100, 110, statistic="mean")
    assert len(result) == 0


def test_get_measurement_in_range_invalid_machine_id(db_connection):
    result = warehouse.get_measurement_in_range(999, "temperature", datetime(2023, 10, 1, 8, 0, 0), datetime(2023, 10, 1, 10, 0, 0), 75, 80, statistic="mean")
    assert len(result) == 0


def test_get_measurement_in_range_invalid_kpi_name(db_connection):
    result = warehouse.get_measurement_in_range(1, "invalid_kpi", datetime(2023, 10, 1, 8, 0, 0), datetime(2023, 10, 1, 10, 0, 0), 75, 80, statistic="mean")
    assert len(result) == 0


def test_get_measurement_in_range_no_kpi_in_range(db_connection):
    result = warehouse.get_measurement_in_range(1, "temperature", datetime(2023, 10, 1, 8, 0, 0), datetime(2023, 10, 1, 10, 0, 0), 0, 10, statistic="mean")
    assert len(result) == 0


def test_get_measurement_in_range_start_time_after_end_time(db_connection):
    result = warehouse.get_measurement_in_range(
        1, "temperature", datetime(2023, 10, 2), datetime(2023, 10, 1), 75, 80, statistic="mean"
    )
    assert len(result) == 0


def test_get_measurement_in_range_no_statistic(db_connection):
    result = warehouse.get_measurement_in_range(1, "temperature", datetime(2023, 10, 1, 8, 0, 0), datetime(2023, 10, 1, 10, 0, 0))
    assert len(result) > 0
    for row in result:
        assert "temperature" in row[2]


def test_get_measurement_with_kpi(db_connection):
    result = warehouse.get_measurement_with_kpi(1, "temperature", datetime(2023, 10, 1, 8, 0, 0), datetime(2023, 10, 1, 10, 0, 0), statistic="mean")
    assert len(result) > 0
    for row in result:
        assert "temperature" in row[2]


def test_get_measurement_with_kpi_no_results(db_connection):
    result = warehouse.get_measurement_with_kpi(1, "nonexistent_kpi", datetime(2023, 10, 1, 8, 0, 0), datetime(2023, 10, 1, 10, 0, 0), statistic="mean")
    assert len(result) == 0


def test_get_measurement_with_kpi_invalid_machine_id(db_connection):
    result = warehouse.get_measurement_with_kpi(999, "temperature", datetime(2023, 10, 1, 8, 0, 0), datetime(2023, 10, 1, 10, 0, 0), statistic="mean")
    assert len(result) == 0


def test_get_measurement_with_kpi_no_kpi_in_time_range(db_connection):
    result = warehouse.get_measurement_with_kpi(
        1, "temperature", datetime(2023, 10, 2), datetime(2023, 10, 3), statistic="mean"
    )
    assert len(result) == 0


def test_get_measurement_with_kpi_start_time_after_end_time(db_connection):
    result = warehouse.get_measurement_with_kpi(
        1, "temperature", datetime(2023, 10, 2), datetime(2023, 10, 1), statistic="mean"
    )
    assert len(result) == 0


def test_get_measurement_with_kpi_no_statistic(db_connection):
    result = warehouse.get_measurement_with_kpi(1, "temperature", datetime(2023, 10, 1, 8, 0, 0), datetime(2023, 10, 1, 10, 0, 0))
    assert len(result) > 0
    for row in result:
        assert "temperature" in row[2]


def test_put_measurement(db_connection):
    timestamp = datetime.now()
    measurements = {"test_kpi": 123}
    warehouse.put_measurement(1, timestamp, measurements)
    result = warehouse.get_measurement_with_kpi(1, "test_kpi", timestamp, timestamp)
    assert len(result) > 0
    assert result[0][2]["test_kpi"] == 123


def test_put_measurement_empty_measurements(db_connection):
    timestamp = datetime.now()
    measurements = {}
    warehouse.put_measurement(1, timestamp, measurements)
    result = warehouse.get_measurement_with_kpi(1, "test_kpi", timestamp, timestamp)
    assert len(result) == 0  # Expect no results since measurements are empty


def test_get_machine_measurements_list(db_connection):
    result = warehouse.get_machine_measurements_list(1)
    assert "temperature" in result


def test_get_machine_measurements_list_no_measurements(db_connection):
    result = warehouse.get_machine_measurements_list(
        999
    )  # Assuming machine ID 999 does not exist
    assert len(result) == 0  # Expect no measurements


def test_get_machine_data_by_id(db_connection):
    result = warehouse.get_machine_data_by_id(1)
    assert len(result) == 1
    assert result[0][1] == "Machine A"


def test_get_machine_data_by_id_nonexistent(db_connection):
    result = warehouse.get_machine_data_by_id(
        999
    )  # Assuming machine ID 999 does not exist
    assert len(result) == 0  # Expect no results


def test_get_machine_data_by_id_invalid_id(db_connection):
    with pytest.raises(psycopg2.Error):
        warehouse.get_machine_data_by_id("invalid_id")  # Passing an invalid ID type


def test_get_all_machines(db_connection):
    result = warehouse.get_all_machines()
    assert len(result) > 0


def test_get_machine_data_by_name(db_connection):
    result = warehouse.get_machine_data_by_name("Machine A")
    assert len(result) == 1
    assert result[0][1] == "Machine A"


def test_get_machine_data_by_name_nonexistent(db_connection):
    result = warehouse.get_machine_data_by_name("Nonexistent Machine")
    assert len(result) == 0  # Expect no results


def test_get_machine_data_by_name_empty_string(db_connection):
    result = warehouse.get_machine_data_by_name("")
    assert len(result) == 0  # Expect no results


def test_put_machine_data(db_connection):
    warehouse.put_machine_data("Machine Z", "Type W", 4, "Factory 3")
    result = warehouse.get_machine_data_by_name("Machine Z")
    assert len(result) == 1
    assert result[0][1] == "Machine Z"


def test_put_machine_data_missing_name(db_connection):
    with pytest.raises(psycopg2.Error):
        warehouse.put_machine_data(None, "Type X", 1, "Factory 1")  # Missing name


def test_delete_machine_by_id(db_connection):
    warehouse.put_machine_data("Machine F", "Type V", 5, "Factory 4")
    result = warehouse.get_machine_data_by_name("Machine F")
    assert len(result) == 1
    warehouse.delete_machine_by_id(result[0][0])
    result = warehouse.get_machine_data_by_name("Machine F")
    assert len(result) == 0


def test_delete_machine_by_id_with_policy_none(db_connection):
    warehouse.put_machine_data("Machine H", "Type Z", 6, "Factory 5")
    result = warehouse.get_machine_data_by_name("Machine H")
    assert len(result) == 1
    machine_id = result[0][0]
    warehouse.delete_machine_by_id(machine_id, policy=None)
    result = warehouse.get_machine_data_by_name("Machine H")
    assert len(result) == 0


def test_delete_machine_by_id_with_policy_cascade(db_connection):
    warehouse.put_machine_data("Machine I", "Type Y", 7, "Factory 6")
    result = warehouse.get_machine_data_by_name("Machine I")
    assert len(result) == 1
    machine_id = result[0][0]

    # Insert related data
    timestamp = datetime.now()
    measurements = {"test_kpi": 123}
    warehouse.put_measurement(1, timestamp, measurements)
    result = warehouse.get_measurement_with_kpi(1, "test_kpi", timestamp, timestamp)
    assert len(result) > 0
    alert_time = datetime.now()
    warehouse.put_alert_data(machine_id, "test_kpi", "test_description", 1, alert_time)

    alerts_result = warehouse.get_alert_by_machine_id(machine_id)
    assert len(alerts_result) > 0

    # Delete machine with CASCADE policy
    warehouse.delete_machine_by_id(machine_id, policy="CASCADE")

    # Verify machine and related data are deleted
    result = warehouse.get_machine_data_by_name("Machine I")
    assert len(result) == 0
    measurements_result = warehouse.get_measurement_with_kpi(machine_id, "test_kpi")
    assert len(measurements_result) == 0
    alerts_result = warehouse.get_alert_by_machine_id(machine_id)
    assert len(alerts_result) == 0


def test_delete_machine_by_id_invalid_id(db_connection):
    with pytest.raises(psycopg2.Error):
        warehouse.delete_machine_by_id("invalid_id")  # Passing an invalid ID type


def test_get_all_alerts(db_connection):
    result = warehouse.get_all_alerts()
    assert len(result) > 0


def test_get_alert_by_id(db_connection):
    # Ensure alert with a specific ID exists
    alert_time = datetime.now()
    warehouse.put_alert_data(1, "test_kpi", "test_description", 1, alert_time)
    result = warehouse.get_alert_by_machine_id(1)
    alert_id = result[-1][0]  # Get the last inserted alert ID
    result = warehouse.get_alert_by_id(alert_id)
    assert len(result) == 1
    assert result[0][0] == alert_id


def test_get_alert_by_id_nonexistent(db_connection):
    result = warehouse.get_alert_by_id(999)  # Assuming alert ID 999 does not exist
    assert len(result) == 0  # Expect no results


def test_get_alert_by_id_invalid_id(db_connection):
    with pytest.raises(psycopg2.Error):
        warehouse.get_alert_by_id("invalid_id")  # Passing an invalid ID type


def test_get_alert_by_machine_id(db_connection):
    result = warehouse.get_alert_by_machine_id(1)
    assert len(result) > 0
    for row in result:
        assert row[1] == 1


def test_get_alert_by_machine_id_nonexistent(db_connection):
    result = warehouse.get_alert_by_machine_id(
        999
    )  # Assuming machine ID 999 does not exist
    assert len(result) == 0  # Expect no results


def test_get_alert_by_machine_id_invalid_id(db_connection):
    with pytest.raises(psycopg2.Error):
        warehouse.get_alert_by_machine_id("invalid_id")  # Passing an invalid ID type


def test_put_alert_data(db_connection):
    alert_time = datetime.now()
    warehouse.put_alert_data(1, "test_kpi", "test_description", 1, alert_time)
    result = warehouse.get_alert_by_machine_id(1)
    conn = warehouse.get_connection()
    conn.commit()
    assert len(result) > 0
    print(result)
    assert result[-1][-1] == "test_description"


def test_put_alert_data_missing_machine_id(db_connection):
    alert_time = datetime.now()
    with pytest.raises(psycopg2.Error):
        warehouse.put_alert_data(
            None, "test_kpi", "test_description", 1, alert_time
        )  # Missing machine ID


def test_put_alert_data_invalid_severity(db_connection):
    alert_time = datetime.now()
    with pytest.raises(psycopg2.Error):
        warehouse.put_alert_data(
            1, "test_kpi", "test_description", 5, alert_time
        )  # Invalid severity


def test_put_alert_data_missing_kpi(db_connection):
    alert_time = datetime.now()
    with pytest.raises(psycopg2.Error):
        warehouse.put_alert_data(1, None, "test_description", 1, alert_time)  # Missing KPI


def test_put_alert_data_missing_description(db_connection):
    alert_time = datetime.now()
    warehouse.put_alert_data(1, "test_kpi", None, 1, alert_time)  # Missing description
    result = warehouse.get_alert_by_machine_id(1)
    assert len(result) > 0
    assert result[-1][-1] is None  # Expect the description to be None


def test_delete_measurement_by_id(db_connection):
    # Insert a measurement to delete
    timestamp = datetime.now()
    measurements = {"test_kpi": 123}
    warehouse.put_measurement(1, timestamp, measurements)
    result = warehouse.get_measurement_with_kpi(1, "test_kpi", timestamp, timestamp)
    assert len(result) > 0
    measurement_id = result[0][1]

    # Delete the measurement
    warehouse.delete_measurement_by_id(measurement_id)
    result = warehouse.get_measurement_with_kpi(1, "test_kpi", timestamp, timestamp)
    assert len(result) == 0  # Expect no results after deletion


def test_delete_measurement_by_id_nonexistent(db_connection):
    # Attempt to delete a nonexistent measurement
    warehouse.delete_measurement_by_id(999999)  # Assuming ID 999999 does not exist
    # No exceptions should be raised
    assert True


def test_delete_measurement_by_id_invalid_id(db_connection):
    # Attempt to delete a measurement with an invalid ID type
    with pytest.raises(psycopg2.Error):
        warehouse.delete_measurement_by_id("invalid_id")  # Passing an invalid ID type
