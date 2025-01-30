CREATE SCHEMA IF NOT EXISTS Warehouse;

DROP TABLE IF EXISTS Warehouse.Alerts;
DROP TABLE IF EXISTS Warehouse.Sensors_Data;
DROP TABLE IF EXISTS historical_store;
DROP TABLE IF EXISTS seasonalities;
DROP TABLE IF EXISTS thresholds;
DROP TABLE IF EXISTS Warehouse.Machines;


CREATE TABLE Warehouse.Machines (
    MachineID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL UNIQUE,
    Line INT NOT NULL DEFAULT 0,
    Factory VARCHAR(255) NOT NULL DEFAULT 'Unknown',
    Type VARCHAR(255) NOT NULL DEFAULT 'Unknown'
);

CREATE TABLE Warehouse.Alerts (
    AlertID SERIAL PRIMARY KEY,
    MachineID INT NOT NULL,
    Timestamp TIMESTAMP NOT NULL,
    Severity INT CHECK (Severity BETWEEN 1 AND 3),
    KPI VARCHAR(255) NOT NULL,
    Description TEXT,
    CONSTRAINT fk_machine FOREIGN KEY (MachineID) REFERENCES Warehouse.Machines(MachineID)
);

CREATE TABLE Warehouse.Sensors_Data (
    Timestamp TIMESTAMP NOT NULL,
    MachineID INT NOT NULL,
    Measurements JSONB,
    PRIMARY KEY (timestamp, MachineID),
    CONSTRAINT fk_machine FOREIGN KEY (MachineID) REFERENCES Warehouse.Machines(MachineID)
);

CREATE TABLE historical_store (
    timestamp TIMESTAMP NOT NULL,
    MachineID INT NOT NULL,
    kpi VARCHAR(255) NOT NULL,
    aggregation_type VARCHAR(5) NOT NULL,
    value DOUBLE PRECISION,
    imputation BOOLEAN,
    anomaly BOOLEAN,
    trend_drift INT,
    next_days_predictions DOUBLE PRECISION[] DEFAULT ARRAY[]::DOUBLE PRECISION[],
    confidence_interval_lower DOUBLE PRECISION[] DEFAULT ARRAY[]::DOUBLE PRECISION[],
    confidence_interval_upper DOUBLE PRECISION[] DEFAULT ARRAY[]::DOUBLE PRECISION[],
    PRIMARY KEY (timestamp, MachineID, kpi, aggregation_type),
    CONSTRAINT fk_machine FOREIGN KEY (MachineID) REFERENCES Warehouse.Machines(MachineID)
);


CREATE TABLE seasonalities (
    timestamp TIMESTAMP NOT NULL,
    MachineID INT NOT NULL,
    kpi VARCHAR(255) NOT NULL,
    aggregation_type VARCHAR(5) NOT NULL,
    selected_f INTEGER,
    PRIMARY KEY (timestamp, MachineID, kpi, aggregation_type),
    CONSTRAINT fk_machine FOREIGN KEY (MachineID) REFERENCES Warehouse.Machines(MachineID)
);

CREATE TABLE thresholds (
    timestamp TIMESTAMP NOT NULL,
    MachineID INT NOT NULL,
    kpi VARCHAR(255) NOT NULL,
    aggregation_type VARCHAR(5) NOT NULL,
    min_threshold DOUBLE PRECISION,
    max_threshold DOUBLE PRECISION,
    PRIMARY KEY (timestamp, MachineID, kpi, aggregation_type),
    CONSTRAINT fk_machine FOREIGN KEY (MachineID) REFERENCES Warehouse.Machines(MachineID)
);

CREATE INDEX idxgin ON Warehouse.Sensors_Data USING GIN (Measurements);