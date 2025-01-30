"""
This module provides functions to interact with a PostgreSQL database for storing and retrieving
machine and sensor data. It includes functions for connecting to the database, inserting and 
retrieving measurements, managing machine records, and handling alerts.
"""

import json
import psycopg2
from psycopg2.extensions import AsIs
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
global conn

host = os.environ["POSTGRES_HOST"] if "POSTGRES_HOST" in os.environ else "localhost"

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host=host,
    database="postgres",
    user="postgres",
    password="password",
    port="5432",
)

# Setting auto commit false
conn.autocommit = True
global cursor
# Creating a cursor object using the cursor() method
cursor = conn.cursor()


def get_connection(
    host=host,
    database="postgres",
    user="postgres",
    password="password",
    port="5432",
):
    """
    Get the connection to the PostgreSQL database.

    Args:
        host (str): The host of the PostgreSQL database.
        database (str): The name of the database.
        user (str): The user to connect to the database.
        password (str): The password to connect to the database.
        port (str): The port of the PostgreSQL database.

    Returns:
        conn: The connection object to the PostgreSQL database.
    """

    global conn
    conn.commit()
    conn.close()
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port,
    )

    # Setting auto commit false
    conn.autocommit = True
    global cursor
    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    return conn


def get_measurement_in_range(
    machine_id,
    kpi_name,
    start_time,
    end_time,
    kpi_start_range=0,
    kpi_end_range=1,
    statistic=None,
):
    """
    Retrieve measurements within a specified range for a given machine and KPI.

    Args:
        machine_id (int): The ID of the machine.
        kpi_name (str): The name of the KPI.
        kpi_start_range (float): The start range of the KPI.
        kpi_end_range (float): The end range of the KPI.
        start_time (datetime, optional): The start time for the query.
        end_time (datetime, optional): The end time for the query.
        statistic (str, optional): The statistic to filter by (e.g., "mean", "max", "min", "sum"). If None, check if KPI exists.

    Returns:
        list: A list of measurements that match the criteria.
    """
    if statistic:
        query = f"SELECT * FROM warehouse.sensors_data WHERE machineid = %s AND (measurements->'{kpi_name}'->>'{statistic}')::NUMERIC >= %s AND (measurements->'{kpi_name}'->>'{statistic}')::NUMERIC <= %s"
        params = [machine_id, kpi_start_range, kpi_end_range]
    else:
        query = f"SELECT * FROM warehouse.sensors_data WHERE machineid = %s AND measurements->'{kpi_name}' IS NOT NULL"
        params = [machine_id]

    if start_time is not None:
        query += " AND timestamp >= %s"
        params.append(start_time)
    if end_time is not None:
        query += " AND timestamp <= %s"
        params.append(end_time)

    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def get_measurement_with_kpi(
    machine_id, kpi_name, start_time=None, end_time=None, statistic=None
):
    """
    Retrieve measurements for a given machine and KPI within a specified time range.

    Args:
        machine_id (int): The ID of the machine.
        kpi_name (str): The name of the KPI.
        start_time (datetime, optional): The start time for the query.
        end_time (datetime, optional): The end time for the query.
        statistic (str, optional): The statistic to filter by (e.g., "mean", "max", "min", "sum"). If None, check if KPI exists.

    Returns:
        list: A list of measurements that match the criteria.
    """
    if statistic:
        query = f"SELECT * FROM warehouse.sensors_data WHERE machineid = %s AND measurements->'{kpi_name}'->>'{statistic}' IS NOT NULL"
        params = [machine_id]
    else:
        query = f"SELECT * FROM warehouse.sensors_data WHERE machineid = %s AND measurements->'{kpi_name}' IS NOT NULL"
        params = [machine_id]

    if start_time is not None:
        query += " AND timestamp >= %s"
        params.append(start_time)
    if end_time is not None:
        query += " AND timestamp <= %s"
        params.append(end_time)

    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def put_measurement(machine_id, timestamp, measurements):
    """
    Insert a new measurement record into the database.

    Args:
        machine_id (int): The ID of the machine.
        timestamp (datetime): The timestamp of the measurement.
        measurements (dict): The measurements data.

    Returns:
        None
    """
    cursor.execute(
        "INSERT INTO warehouse.sensors_data (machineid, timestamp, measurements) VALUES (%s, %s, %s)",
        (machine_id, timestamp, json.dumps(measurements)),
    )
    conn.commit()


def delete_measurement_by_id(machine_id):
    """
    Delete measurement records for a given machine ID.

    Args:
        machine_id (int): The ID of the machine.

    Returns:
        None
    """
    cursor.execute(
        "DELETE FROM warehouse.sensors_data WHERE machineid = %s",
        (machine_id,),
    )


def get_machine_measurements_list(machine_id):
    """
    Retrieve a list of distinct measurement keys for a given machine.

    Args:
        machine_id (int): The ID of the machine.

    Returns:
        list: A list of distinct measurement keys.
    """
    cursor.execute(
        "SELECT DISTINCT jsonb_object_keys(measurements) FROM warehouse.sensors_data WHERE machineid = %s",
        (machine_id,),
    )
    return [row[0] for row in cursor.fetchall()]


def get_machine_data_by_id(machine_id):
    """
    Retrieve machine data for a given machine ID.

    Args:
        machine_id (int): The ID of the machine.

    Returns:
        list: A list of machine data records.
    """
    cursor.execute(
        "SELECT * FROM warehouse.machines WHERE machineid = %s",
        (machine_id,),
    )
    return cursor.fetchall()


def get_all_machines():
    """
    Retrieve data for all machines.

    Returns:
        list: A list of all machine data records.
    """
    cursor.execute("SELECT * FROM warehouse.machines")
    return cursor.fetchall()


def get_machine_data_by_name(machine_name):
    """
    Retrieve machine data for a given machine name.

    Args:
        machine_name (str): The name of the machine.

    Returns:
        list: A list of machine data records.
    """
    cursor.execute(
        "SELECT * FROM warehouse.machines WHERE name = %s",
        (machine_name,),
    )
    return cursor.fetchall()


def put_machine_data(
    machine_name, machine_type=None, machine_line=None, machine_factory=None
):
    """
    Insert a new machine record into the database.

    Args:
        machine_name (str): The name of the machine.
        machine_type (str, optional): The type of the machine.
        machine_line (int, optional): The line of the machine.
        machine_factory (str, optional): The factory of the machine.

    Returns:
        int: The ID of the inserted machine record, or None if insertion failed.
    """
    columns = ["name"]
    values = [machine_name]

    if machine_type is not None:
        columns.append("type")
        values.append(machine_type)
    if machine_line is not None:
        columns.append("line")
        values.append(machine_line)
    if machine_factory is not None:
        columns.append("factory")
        values.append(machine_factory)

    query = "INSERT INTO warehouse.machines (%s) VALUES %s  RETURNING machineid"
    cursor.execute(query, (AsIs(",".join(columns)), tuple(values)))
    conn.commit()
    result = cursor.fetchone()
    return result[0] if result else None


def put_machine_with_id(
    machine_id, machine_name, machine_type=None, machine_line=None, machine_factory=None
):
    """
    Insert a new machine record into the database with a specified ID.

    Args:
        machine_id (int): The ID of the machine.
        machine_name (str): The name of the machine.
        machine_type (str, optional): The type of the machine.
        machine_line (int, optional): The line of the machine.
        machine_factory (str, optional): The factory of the machine.

    Returns:
        None
    """
    columns = ["machineid", "name"]
    values = [machine_id, machine_name]

    if machine_type is not None:
        columns.append("type")
        values.append(machine_type)

    if machine_line is not None:
        columns.append("line")
        values.append(machine_line)
    if machine_factory is not None:
        columns.append("factory")
        values.append(machine_factory)

    query = "INSERT INTO warehouse.machines (%s) VALUES %s Returning machineid"
    cursor.execute(query, (AsIs(",".join(columns)), tuple(values)))
    result = cursor.fetchone()
    conn.commit()
    return result[0] if result else None

def put_machine_with_default_id(
    machine_name, machine_type=None, machine_line=None, machine_factory=None
):
    """
    Insert a new machine record into the database with default ID.

    Args:
        machine_name (str): The name of the machine.
        machine_type (str, optional): The type of the machine.
        machine_line (int, optional): The line of the machine.
        machine_factory (str, optional): The factory of the machine.

    Returns:
        int: The ID of the inserted machine record, or None if insertion failed.
    """
    columns = ["name"]
    values = [machine_name]

    if machine_type is not None:
        columns.append("type")
        values.append(machine_type)

    if machine_line is not None:
        columns.append("line")
        values.append(machine_line)
    if machine_factory is not None:
        columns.append("factory")
        values.append(machine_factory)

    query = "INSERT INTO warehouse.machines (%s) VALUES %s Returning machineid"
    cursor.execute(query, (AsIs(",".join(columns)), tuple(values)))
    result = cursor.fetchone()
    conn.commit()
    return result[0] if result else None

def delete_machine_by_id(machine_id, policy=None):
    """
    Delete a machine record by machine ID, with optional cascading delete policy.

    Args:
        machine_id (int): The ID of the machine.
        policy (str, optional): The delete policy ("CASCADE" for cascading delete).

    Returns:
        None
    """
    if policy == "CASCADE":
        cursor.execute(
            "DELETE FROM warehouse.alerts WHERE machineid = %s", (machine_id,)
        )
        cursor.execute(
            "DELETE FROM warehouse.sensors_data WHERE machineid = %s", (machine_id,)
        )
    cursor.execute("DELETE FROM warehouse.machines WHERE machineid = %s", (machine_id,))


def get_all_alerts():
    """
    Retrieve all alert records.

    Returns:
        list: A list of all alert records.
    """
    cursor.execute("SELECT * FROM warehouse.alerts")
    return cursor.fetchall()


def get_alert_by_id(alert_id):
    """
    Retrieve an alert record by alert ID.

    Args:
        alert_id (int): The ID of the alert.

    Returns:
        list: A list of alert records that match the criteria.
    """
    cursor.execute(
        "SELECT * FROM warehouse.alerts WHERE alertid = %s",
        (alert_id,),
    )
    return cursor.fetchall()


def get_alert_by_machine_id(machine_id):
    """
    Retrieve alert records for a given machine ID.

    Args:
        machine_id (int): The ID of the machine.

    Returns:
        list: A list of alert records that match the criteria.
    """
    cursor.execute(
        "SELECT * FROM warehouse.alerts WHERE machineid = %s",
        (machine_id,),
    )
    return cursor.fetchall()


def put_alert_data(
    machine_id, alert_kpi, alert_description, alert_severity, alert_time
):
    """
    Insert a new alert record into the database.

    Args:
        machine_id (int): The ID of the machine.
        alert_kpi (str): The KPI associated with the alert.
        alert_description (str): The description of the alert.
        alert_severity (int): The severity of the alert (1 to 3).
        alert_time (datetime): The timestamp of the alert.

    Returns:
        None
    """
    cursor.execute(
        "INSERT INTO warehouse.alerts (machineid, kpi, description, severity, timestamp) VALUES (%s, %s, %s, %s, %s)",
        (machine_id, alert_kpi, alert_description, alert_severity, alert_time),
    )
    conn.commit()


def delete_alerts_by_machine_id(machine_id):
    """
    Delete alert records for a given machine ID.

    Args:
        machine_id (int): The ID of the machine.

    Returns:
        None
    """
    query = f"DELETE FROM warehouse.alerts WHERE machineid = %s"
    cursor.execute(query, (machine_id,))


def get_alerts_by_line(line):
    """
    Retrieve alert records for a given line.

    Args:
        line (int): The line of the machine.

    Returns:
        list: A list of alert records that match the criteria.
    """
    cursor.execute(
        "SELECT * FROM warehouse.alerts WHERE machineid IN (SELECT machineid FROM warehouse.machines WHERE line = %s)",
        (line,),
    )
    return cursor.fetchall()
