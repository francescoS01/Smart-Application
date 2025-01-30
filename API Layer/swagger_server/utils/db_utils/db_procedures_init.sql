
-- Creates functions for the API Layer to easily interact with the database and reuse code
-- This script should be run the first time the API connects to the database

-- Function to get machine data with optional filters on id, type, line, and factory
CREATE OR REPLACE FUNCTION get_machines(
    IN machine_ids INT[] DEFAULT NULL,
    IN machine_types VARCHAR(255)[] DEFAULT NULL,
    IN machine_lines INT[] DEFAULT NULL,
    IN machine_factories VARCHAR(255)[] DEFAULT NULL
)
RETURNS TABLE (
    MachineID INT,
    Name VARCHAR(255),
    Line INT,
    Factory VARCHAR(255),
    Type VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        Machines.MachineID::INT,
        Machines.Name,
        Machines.Line,
        Machines.Factory,
        Machines.Type
    FROM Warehouse.Machines
    WHERE
        (machine_ids IS NULL OR Machines.MachineID::INT = ANY (CAST(machine_ids AS INT[]))) AND
        (machine_types IS NULL OR Machines.Type = ANY (CAST(machine_types AS VARCHAR(255)[]))) AND
        (machine_lines IS NULL OR Machines.Line = ANY (CAST(machine_lines AS INT[]))) AND
        (machine_factories IS NULL OR Machines.Factory = ANY (CAST(machine_factories AS VARCHAR(255)[])));
END;
$$;

-- Function to insert a new machine into the database
-- If the machine name already exists, returns error code -1, otherwise returns the new machine ID
CREATE OR REPLACE FUNCTION insert_machine(
    IN machine_name VARCHAR(255),
    IN machine_line INT,
    IN machine_factory VARCHAR(255),
    IN machine_type VARCHAR(255)
)
RETURNS TABLE (
    newID INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM Warehouse.Machines WHERE Name = machine_name) THEN
        RETURN QUERY SELECT -1;
        RETURN;
    END IF;

    RETURN QUERY
    INSERT INTO Warehouse.Machines (MachineID, Name, Line, Factory, Type)
    VALUES (DEFAULT, machine_name, machine_line, machine_factory, machine_type)
    RETURNING MachineID;
END;
$$;

-- Function to update an existing machine in the database with optional parameters
-- If the new machine name already exists, returns error code -1, otherwise returns 0
CREATE OR REPLACE FUNCTION update_machine(
    IN machine_id INT,
    IN machine_name VARCHAR(255),
    IN machine_line INT,
    IN machine_factory VARCHAR(255),
    IN machine_type VARCHAR(255)
)
RETURNS TABLE (
    code INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM Warehouse.Machines WHERE Name = machine_name AND MachineID != machine_id) THEN
        RETURN QUERY SELECT -1;
        RETURN;
    END IF;
    UPDATE Warehouse.Machines
    SET
        Name = COALESCE(machine_name, Name),
        Line = COALESCE(machine_line, Line),
        Factory = COALESCE(machine_factory, Factory),
        Type = COALESCE(machine_type, Type)
    WHERE MachineID = machine_id;
    RETURN QUERY SELECT 0;
END;
$$;

-- Function to delete a machine from the database
-- If the machine does not exist, returns error code -1, otherwise returns 0
CREATE OR REPLACE FUNCTION delete_machine(
    IN machine_id INT
)
RETURNS TABLE (
    code INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Warehouse.Machines WHERE MachineID = machine_id) THEN
        RETURN QUERY SELECT -1;
        RETURN;
    END IF;
    DELETE FROM Warehouse.Alerts
    WHERE MachineID = machine_id;
    DELETE FROM Warehouse.Sensors_Data
    WHERE MachineID = machine_id;
    DELETE FROM Warehouse.Machines
    WHERE MachineID = machine_id;
    RETURN QUERY SELECT 0;
END;
$$;

-- Function to get machine status (a machine is considered idle if it has no sensor data in the last 30 hours)
-- In input, the Function takes a timestamp to check the status of the machines at that time and an optional list of machine IDs that, if null, will return the status of all machines
CREATE OR REPLACE FUNCTION get_machine_status(
    IN machine_ids INT[] DEFAULT NULL
)
RETURNS TABLE (
    MachineID INT,
    Status TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        Machines.MachineID::INT,
        CASE
            WHEN MAX(Sensors_Data.Timestamp) IS NULL OR MAX(Sensors_Data.Timestamp) < NOW() - INTERVAL '30 hours' THEN 'idle'
            ELSE 'operational'
        END AS Status
    FROM Warehouse.Machines
    LEFT JOIN Warehouse.Sensors_Data ON Machines.MachineID::INT = Sensors_Data.MachineID
    WHERE
        (machine_ids IS NULL OR Machines.MachineID::INT = ANY (CAST(machine_ids AS INT[])))
    GROUP BY Machines.MachineID;
END;
$$;

-- Function to get both machine data and its status filtered by optional parameters (id, type, line, factory, and status)
CREATE OR REPLACE FUNCTION get_machines_with_status(
    IN machine_ids INT[] DEFAULT NULL,
    IN machine_types VARCHAR(255)[] DEFAULT NULL,
    IN machine_lines INT[] DEFAULT NULL,
    IN machine_factories VARCHAR(255)[] DEFAULT NULL,
    IN machine_status BOOLEAN DEFAULT FALSE
)
RETURNS TABLE (
    MachineID INT,
    Name VARCHAR(255),
    Line INT,
    Factory VARCHAR(255),
    Type VARCHAR(255),
    Status TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    -- create a temporary table to store the machine status
    WITH FilteredMachineNoStatus AS (
        SELECT
            Machines.MachineID::INT AS MachineID,
            Machines.Name AS Name,
            Machines.Line AS Line,
            Machines.Factory AS Factory,
            Machines.type AS Type
        FROM Warehouse.Machines
        WHERE
            (machine_ids IS NULL OR Machines.MachineID::INT = ANY (CAST(machine_ids AS INT[]))) AND
            (machine_types IS NULL OR Machines.Type = ANY (CAST(machine_types AS VARCHAR(255)[]))) AND
            (machine_lines IS NULL OR Machines.Line = ANY (CAST(machine_lines AS INT[]))) AND
            (machine_factories IS NULL OR Machines.Factory = ANY (CAST(machine_factories AS VARCHAR(255)[])))
    ),
    MachineStatus AS (
        SELECT
            FilteredMachineNoStatus.MachineID,
            CASE
                WHEN MAX(Sensors_Data.Timestamp) IS NULL OR MAX(Sensors_Data.Timestamp) < NOW() - INTERVAL '30 hours' THEN 'idle'
                ELSE 'operational'
            END AS Status
        FROM FilteredMachineNoStatus
        LEFT JOIN Warehouse.Sensors_Data ON FilteredMachineNoStatus.MachineID = Sensors_Data.MachineID
        GROUP BY FilteredMachineNoStatus.MachineID
    )
    SELECT
        FilteredMachineNoStatus.MachineID,
        FilteredMachineNoStatus.Name,
        FilteredMachineNoStatus.Line,
        FilteredMachineNoStatus.Factory,
        FilteredMachineNoStatus.Type,
        MachineStatus.Status
    FROM FilteredMachineNoStatus
    LEFT JOIN MachineStatus ON FilteredMachineNoStatus.MachineID = MachineStatus.MachineID
    WHERE
        machine_status IS NULL OR (machine_status = TRUE AND MachineStatus.Status = 'operational') OR (machine_status = FALSE AND MachineStatus.Status = 'idle');
END;
$$;

-- Function to get sensor data for specific machines with filters on time window, id, and KPI. The time window is interpreted as [start_time, end_time)
-- Aggregation type indicates to retrieve the corresponding entry of kpi JSONB object
CREATE OR REPLACE FUNCTION get_sensor_data(
    IN start_time TIMESTAMP DEFAULT NULL,
    IN end_time TIMESTAMP DEFAULT NULL,
    IN machine_ids INT[] DEFAULT NULL,
    IN kpi_names VARCHAR(255)[] DEFAULT NULL,
    IN aggregation_type VARCHAR(4) DEFAULT 'sum'
)
RETURNS TABLE (
    MachineID INT,
    Timestamp_t TIMESTAMP,
    KPI VARCHAR(255),
    Value FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        Sensors_Data.MachineID::INT,
        Sensors_Data.Timestamp::TIMESTAMP,
        kpi_data.kpi_name::VARCHAR(255),
        (kpi_data.kpi_measurement->>aggregation_type)::FLOAT AS Value
    FROM Warehouse.Sensors_Data
    CROSS JOIN LATERAL jsonb_each(Sensors_Data.Measurements::JSONB) AS kpi_data(kpi_name, kpi_measurement)
    WHERE
        (start_time IS NULL OR Sensors_Data.Timestamp >= start_time) AND
        (end_time IS NULL OR Sensors_Data.Timestamp < end_time) AND
        (machine_ids IS NULL OR Sensors_Data.MachineID = ANY (CAST(machine_ids AS INT[]))) AND
        (kpi_names IS NULL OR kpi_data.kpi_name = ANY (CAST(kpi_names AS VARCHAR(255)[]))) AND
        kpi_data.kpi_measurement ? aggregation_type
    ORDER BY Sensors_Data.Timestamp;
END;
$$;

-- Get preprocessed sensors data for specific machines with filters on time window, id, and KPI according to the specified aggregation type. The time window is interpreted as [start_time, end_time)
CREATE OR REPLACE FUNCTION get_preprocessed_data(
    IN start_time TIMESTAMP DEFAULT NULL,
    IN end_time TIMESTAMP DEFAULT NULL,
    IN machine_ids INT[] DEFAULT NULL,
    IN kpi_names VARCHAR(255)[] DEFAULT NULL,
    IN aggregation_type_par VARCHAR(4) DEFAULT 'sum'
)
RETURNS TABLE (
    MachineID INT,
    Timestamp_t TIMESTAMP,
    KPI VARCHAR(255),
    Value FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        historical_store.MachineID::INT,
        historical_store.timestamp::TIMESTAMP,
        historical_store.kpi::VARCHAR(255),
        (historical_store.value)::FLOAT AS Value
    FROM historical_store
    WHERE
        (start_time IS NULL OR historical_store.timestamp >= start_time) AND
        (end_time IS NULL OR historical_store.timestamp < end_time) AND
        (machine_ids IS NULL OR historical_store.MachineID = ANY (CAST(machine_ids AS INT[]))) AND
        (kpi_names IS NULL OR historical_store.kpi = ANY (CAST(kpi_names AS VARCHAR(255)[]))) AND
        historical_store.aggregation_type = aggregation_type_par
    ORDER BY historical_store.timestamp;
END;
$$;

-- Function to get alerts based on alert IDs
CREATE OR REPLACE FUNCTION get_alerts(
    IN alert_ids INT[] DEFAULT NULL
)
RETURNS TABLE (
    AlertID INT,
    MachineID INT,
    Timestamp_t TIMESTAMP,
    Severity INT,
    KPI VARCHAR(255),
    Description TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        Alerts.AlertID,
        Alerts.MachineID,
        Alerts.Timestamp,
        Alerts.Severity,
        Alerts.KPI,
        Alerts.Description
    FROM Warehouse.Alerts
    WHERE
        (alert_ids IS NULL OR Alerts.AlertID = ANY (CAST(alert_ids AS INT[])));
END;
$$;

-- Function to get alerts with optional filters on machines, severity and time window
CREATE OR REPLACE FUNCTION get_alerts_filtered(
   IN machines INT[] DEFAULT NULL,
   IN severity_s INT DEFAULT NULL,
   IN start_time TIMESTAMP DEFAULT NULL,
   IN end_time TIMESTAMP DEFAULT NULL
)
RETURNS TABLE (
   AlertID INT,
   Timestamp_t TIMESTAMP,
   MachineID INT,
   Severity INT,
   Description TEXT,
   KPI VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
   RETURN QUERY
   SELECT
       Alerts.AlertID,
       Alerts.Timestamp,
       Alerts.MachineID,
       Alerts.Severity,
       Alerts.Description,
       Alerts.KPI
   FROM Warehouse.Alerts
   WHERE
       (machines IS NULL OR Alerts.MachineID = ANY (CAST(machines AS INT[]))) AND
       (severity_s IS NULL OR Alerts.Severity = CAST(severity_s AS INT)) AND
       (start_time IS NULL OR Alerts.Timestamp >= start_time) AND
       (end_time IS NULL OR Alerts.Timestamp <= end_time);
END;
$$;

-- Function to insert a new alert into the database returning the new alert ID
CREATE OR REPLACE FUNCTION insert_alert(
    IN machine_id INT,
    IN alert_timestamp TIMESTAMP,
    IN alert_severity INT,
    IN alert_kpi VARCHAR(255),
    IN alert_description TEXT
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    alert_id_new INTEGER;
BEGIN
    INSERT INTO Warehouse.Alerts (AlertID, MachineID, Timestamp, Severity, KPI, Description)
    VALUES (DEFAULT, machine_id, alert_timestamp, alert_severity, alert_kpi, alert_description)
    RETURNING AlertID INTO alert_id_new;
    RETURN alert_id_new;
END;
$$;

-- Function to get the name of a machine given its ID
CREATE OR REPLACE FUNCTION get_machine_name(
    IN machine_id INT
)
RETURNS TABLE (
    Name VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        Machines.Name
    FROM Warehouse.Machines
    WHERE
        Machines.MachineID::INT = machine_id;
END;
$$;

-- Function to get the machine type given its ID
CREATE OR REPLACE FUNCTION get_machine_type(
    IN machine_id INT
)
RETURNS VARCHAR(255)
LANGUAGE plpgsql
AS $$
DECLARE
    machine_type VARCHAR(255);
BEGIN
    -- If the machine does not exist, return NULL
    SELECT Machines.Type INTO machine_type
    FROM Warehouse.Machines
    WHERE Machines.MachineID::INT = machine_id;
    RETURN machine_type;
END;
$$;

DROP FUNCTION IF EXISTS get_machine_ids_from_types(VARCHAR(255)[]);

-- Function to get machine ids from given machine types
CREATE OR REPLACE FUNCTION get_machine_ids_and_name_from_types(
    IN machine_types VARCHAR(255)[] DEFAULT NULL
)
RETURNS TABLE (
    MachineID INT,
    Name VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        Machines.MachineID::INT, Machines.Name
    FROM Warehouse.Machines
    WHERE
        (machine_types IS NULL OR Machines.Type = ANY (CAST(machine_types AS VARCHAR(255)[])));
END;
$$;

-- Get machines not in the given list of machine IDs
CREATE OR REPLACE FUNCTION get_machines_not_in_list(
    IN machine_ids INT[] DEFAULT NULL
)
RETURNS TABLE (
    MachineID INT,
    Name VARCHAR(255),
    Line INT,
    Factory VARCHAR(255),
    Type VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        Machines.MachineID::INT,
        Machines.Name,
        Machines.Line,
        Machines.Factory,
        Machines.Type
    FROM Warehouse.Machines
    WHERE
        (machine_ids IS NULL OR Machines.MachineID::INT != ALL (CAST(machine_ids AS INT[])));
END;
$$;
