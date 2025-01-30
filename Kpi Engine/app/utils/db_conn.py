import psycopg2
import sys,os
sys.path.append(os.path.join("..",'..','..','Storage'))
import warehouse
from datetime import datetime


def execute_sql_script(file_path):
    """
    Execyte remote sql script
    """
    try:
        # Establish the connection
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="password",
            port="5432",
        )
        conn.autocommit = True  # Automatically commit changes
        cur = conn.cursor()

        # Open and read the SQL script
        with open(file_path, "r") as sql_file:
            sql_script = sql_file.read()

        # Execute the SQL script
        cur.execute(sql_script)
        print(f"Successfully executed the script: {file_path}")

        # Close the cursor and connection
        cur.close()
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}") 

conn=warehouse.get_connection()

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="password",
    port="5432",
)

# Setting auto commit false
conn.autocommit = True
global cursor
def get_measurements_in_range(
    machine_id,
    kpi_names,
    start_time=None,
    end_time=None,
    kpi_start_range=0,
    kpi_end_range=1,
):
    """
    Retrieve measurements within a specified range for a given machine and list of KPIs.

    Args:
        machine_id (str): The ID of the machine.
        kpi_names (list of str): A list of KPI names to filter.
        kpi_start_range (float): The start range of the KPI values.
        kpi_end_range (float): The end range of the KPI values.
        start_time (datetime, optional): The start time for the query.
        end_time (datetime, optional): The end time for the query.

    Returns:
        list: A list of measurements that match the criteria.
    """
    if not kpi_names:
        raise ValueError("The kpi_names list cannot be empty.")

    # Start building the query
    query = """
        SELECT *
        FROM warehouse.sensors_data
        WHERE machineid = %s
    """
    params = [machine_id]

    # Add KPI conditions
    kpi_conditions = []
    for kpi_name in kpi_names:
        condition = f"(measurements->>%s)::NUMERIC >= %s AND (measurements->>%s)::NUMERIC <= %s"
        kpi_conditions.append(condition)
        params.extend([kpi_name, kpi_start_range, kpi_name, kpi_end_range])

    # Combine KPI conditions using OR
    if kpi_conditions:
        query += " AND (" + " OR ".join(kpi_conditions) + ")"

    # Add time range conditions if provided
    if start_time is not None:
        query += " AND timestamp >= %s"
        params.append(start_time)
    if end_time is not None:
        query += " AND timestamp <= %s"
        params.append(end_time)

    # Execute the query
    cursor.execute(query, tuple(params))
    return cursor.fetchall()
# Creating a cursor object using the cursor() method
cursor = conn.cursor()
def test():
    query = "SELECT * FROM warehouse.sensors_data"
    cursor.execute(query)
    return cursor.fetchall()



for val in get_measurements_in_range(
    machine_id=1,
    kpi_names=['cost','cost_idle','temperature'],
    start_time=datetime(year=2023,month=9,day=1),
    end_time=datetime(year=2025,month=9,day=1)
):
    print(val)
