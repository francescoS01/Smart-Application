-- Populate Machines table
INSERT INTO Warehouse.Machines (MachineID, Name, Line, Factory, Type) VALUES
(1, 'Machine A', 1, 'Factory 1', 'Type X'),
(2, 'Machine B', 2, 'Factory 1', 'Type Y'),
(3, 'Machine C', 1, 'Factory 2', 'Type X'),
(4, 'Machine D', 3, 'Factory 2', 'Type Z');

-- Populate Alerts table
INSERT INTO Warehouse.Alerts (AlertID, MachineID, Timestamp, Severity, KPI, Description) VALUES
(DEFAULT, 1, '2023-10-01 08:00:00', 2, 'Temperature', 'Temperature exceeded threshold'),
(DEFAULT, 1, '2023-10-01 09:00:00', 1, 'Pressure', 'Pressure below threshold'),
(DEFAULT, 2, '2023-10-01 10:00:00', 3, 'Vibration', 'Vibration level critical'),
(DEFAULT, 2, '2023-10-01 11:00:00', 2, 'Humidity', 'Humidity level high'),
(DEFAULT, 3, '2023-10-01 12:00:00', 2, 'Temperature', 'Temperature exceeded threshold'),
(DEFAULT, 3, '2023-10-01 13:00:00', 1, 'Pressure', 'Pressure below threshold'),
(DEFAULT, 4, '2023-10-01 14:00:00', 3, 'Vibration', 'Vibration level critical'),
(DEFAULT, 4, '2023-10-01 15:00:00', 2, 'Humidity', 'Humidity level high');

-- Populate Sensors_Data table
INSERT INTO Warehouse.Sensors_Data (Timestamp, MachineID, Measurements) VALUES
('2023-10-01 08:00:00', 1, '{"temperature": {"mean": 75.5, "max": 76.0, "min": 75.0, "sum": 226.5}, "consumption": {"mean": 50.2, "max": 51.0, "min": 49.5, "sum": 150.6}, "power": {"mean": 10.5, "max": 10.7, "min": 10.3, "sum": 31.5}}'),
('2023-10-01 09:00:00', 1, '{"temperature": {"mean": 76.0, "max": 76.5, "min": 75.5, "sum": 228.0}, "consumption": {"mean": 51.0, "max": 51.5, "min": 50.5, "sum": 153.0}, "power": {"mean": 10.7, "max": 11.0, "min": 10.5, "sum": 32.1}}'),
('2023-10-01 10:00:00', 1, '{"temperature": {"mean": 77.1, "max": 77.5, "min": 76.5, "sum": 231.3}, "consumption": {"mean": 52.3, "max": 52.5, "min": 52.0, "sum": 156.9}, "power": {"mean": 11.0, "max": 11.2, "min": 10.8, "sum": 33.0}}'),
('2023-10-01 08:00:00', 2, '{"temperature": {"mean": 70.2, "max": 70.5, "min": 70.0, "sum": 210.6}, "consumption": {"mean": 45.1, "max": 45.5, "min": 44.8, "sum": 135.3}, "power": {"mean": 9.8, "max": 10.0, "min": 9.5, "sum": 29.4}}'),
('2023-10-01 09:00:00', 2, '{"temperature": {"mean": 71.0, "max": 71.5, "min": 70.5, "sum": 213.0}, "consumption": {"mean": 46.0, "max": 46.5, "min": 45.5, "sum": 138.0}, "power": {"mean": 10.0, "max": 10.3, "min": 9.8, "sum": 30.0}}'),
('2023-10-01 10:00:00', 2, '{"temperature": {"mean": 72.5, "max": 73.0, "min": 72.0, "sum": 217.5}, "consumption": {"mean": 47.2, "max": 47.5, "min": 47.0, "sum": 141.6}, "power": {"mean": 10.3, "max": 10.5, "min": 10.0, "sum": 30.9}}'),
('2023-10-01 08:00:00', 3, '{"temperature": {"mean": 80.1, "max": 80.5, "min": 79.5, "sum": 240.3}, "consumption": {"mean": 55.0, "max": 55.5, "min": 54.5, "sum": 165.0}, "power": {"mean": 11.5, "max": 11.8, "min": 11.2, "sum": 34.5}}'),
('2023-10-01 09:00:00', 3, '{"temperature": {"mean": 81.0, "max": 81.5, "min": 80.5, "sum": 243.0}, "consumption": {"mean": 56.2, "max": 56.5, "min": 56.0, "sum": 168.6}, "power": {"mean": 11.8, "max": 12.0, "min": 11.5, "sum": 35.4}}'),
('2023-10-01 10:00:00', 3, '{"temperature": {"mean": 82.3, "max": 82.5, "min": 82.0, "sum": 246.9}, "consumption": {"mean": 57.5, "max": 58.0, "min": 57.0, "sum": 172.5}, "power": {"mean": 12.0, "max": 12.3, "min": 11.8, "sum": 36.0}}'),
('2023-10-01 08:00:00', 4, '{"temperature": {"mean": 72.3, "max": 72.5, "min": 72.0, "sum": 216.9}, "consumption": {"mean": 48.0, "max": 48.5, "min": 47.5, "sum": 144.0}, "power": {"mean": 10.5, "max": 10.8, "min": 10.3, "sum": 31.5}}'),
('2023-10-01 09:00:00', 4, '{"temperature": {"mean": 73.0, "max": 73.5, "min": 72.5, "sum": 219.0}, "consumption": {"mean": 49.1, "max": 49.5, "min": 48.5, "sum": 147.3}, "power": {"mean": 10.7, "max": 11.0, "min": 10.5, "sum": 32.1}}'),
('2023-10-01 10:00:00', 4, '{"temperature": {"mean": 74.1, "max": 74.5, "min": 73.5, "sum": 222.3}, "consumption": {"mean": 50.3, "max": 50.5, "min": 50.0, "sum": 150.9}, "power": {"mean": 11.0, "max": 11.3, "min": 10.8, "sum": 33.0}}'),
('2023-10-01 11:00:00', 1, '{"offline_time": {"mean": 10, "max": 10, "min": 10, "sum": 10}, "cost": {"mean": 5.0, "max": 5.0, "min": 5.0, "sum": 5.0}, "cost_idle": {"mean": 1.0, "max": 1.0, "min": 1.0, "sum": 1.0}, "cost_working": {"mean": 4.0, "max": 4.0, "min": 4.0, "sum": 4.0}}'),
('2023-10-01 12:00:00', 1, '{"offline_time": {"mean": 15, "max": 15, "min": 15, "sum": 15}, "cost": {"mean": 6.0, "max": 6.0, "min": 6.0, "sum": 6.0}, "cost_idle": {"mean": 1.5, "max": 1.5, "min": 1.5, "sum": 1.5}, "cost_working": {"mean": 4.5, "max": 4.5, "min": 4.5, "sum": 4.5}}'),
('2023-10-01 13:00:00', 1, '{"offline_time": {"mean": 20, "max": 20, "min": 20, "sum": 20}, "cost": {"mean": 7.0, "max": 7.0, "min": 7.0, "sum": 7.0}, "cost_idle": {"mean": 2.0, "max": 2.0, "min": 2.0, "sum": 2.0}, "cost_working": {"mean": 5.0, "max": 5.0, "min": 5.0, "sum": 5.0}}'),
('2023-10-01 11:00:00', 2, '{"cycles": {"mean": 100, "max": 100, "min": 100, "sum": 100}, "good_cycles": {"mean": 95, "max": 95, "min": 95, "sum": 95}, "bad_cycles": {"mean": 5, "max": 5, "min": 5, "sum": 5}, "average_cycle_time": {"mean": 1.2, "max": 1.2, "min": 1.2, "sum": 1.2}}'),
('2023-10-01 12:00:00', 2, '{"cycles": {"mean": 110, "max": 110, "min": 110, "sum": 110}, "good_cycles": {"mean": 105, "max": 105, "min": 105, "sum": 105}, "bad_cycles": {"mean": 5, "max": 5, "min": 5, "sum": 5}, "average_cycle_time": {"mean": 1.1, "max": 1.1, "min": 1.1, "sum": 1.1}}'),
('2023-10-01 13:00:00', 2, '{"cycles": {"mean": 120, "max": 120, "min": 120, "sum": 120}, "good_cycles": {"mean": 115, "max": 115, "min": 115, "sum": 115}, "bad_cycles": {"mean": 5, "max": 5, "min": 5, "sum": 5}, "average_cycle_time": {"mean": 1.0, "max": 1.0, "min": 1.0, "sum": 1.0}}'),
('2023-10-01 11:00:00', 3, '{"acceleration_x": {"mean": 0.5, "max": 0.5, "min": 0.5, "sum": 0.5}, "acceleration_y": {"mean": 0.6, "max": 0.6, "min": 0.6, "sum": 0.6}, "acceleration_z": {"mean": 0.7, "max": 0.7, "min": 0.7, "sum": 0.7}}'),
('2023-10-01 12:00:00', 3, '{"acceleration_x": {"mean": 0.6, "max": 0.6, "min": 0.6, "sum": 0.6}, "acceleration_y": {"mean": 0.7, "max": 0.7, "min": 0.7, "sum": 0.7}, "acceleration_z": {"mean": 0.8, "max": 0.8, "min": 0.8, "sum": 0.8}}'),
('2023-10-01 13:00:00', 3, '{"acceleration_x": {"mean": 0.7, "max": 0.7, "min": 0.7, "sum": 0.7}, "acceleration_y": {"mean": 0.8, "max": 0.8, "min": 0.8, "sum": 0.8}, "acceleration_z": {"mean": 0.9, "max": 0.9, "min": 0.9, "sum": 0.9}}');

-- Populate historical_store table
INSERT INTO historical_store (timestamp, MachineID, kpi, aggregation_type, value, imputation, anomaly, trend_drift, next_days_predictions, confidence_interval_lower, confidence_interval_upper) VALUES
('2023-10-01 00:00:00', 1, 'temperature', 'avg', 75.5, FALSE, FALSE, 0, ARRAY[75.5, 75.6, 75.7, 75.8, 75.9, 76.0, 76.1, 76.2, 76.3, 76.4, 76.5, 76.6, 76.7, 76.8, 76.9, 77.0, 77.1, 77.2, 77.3, 77.4, 77.5], ARRAY[75.4, 75.5, 75.6, 75.7, 75.8, 75.9, 76.0, 76.1, 76.2, 76.3, 76.4, 76.5, 76.6, 76.7, 76.8, 76.9, 77.0, 77.1, 77.2, 77.3, 77.4], ARRAY[75.6, 75.7, 75.8, 75.9, 76.0, 76.1, 76.2, 76.3, 76.4, 76.5, 76.6, 76.7, 76.8, 76.9, 77.0, 77.1, 77.2, 77.3, 77.4, 77.5, 77.6]),
('2023-10-01 00:00:00', 1, 'temperature', 'sum', 76.0, FALSE, FALSE, 0, ARRAY[76.0, 76.1, 76.2, 76.3, 76.4, 76.5, 76.6, 76.7, 76.8, 76.9, 77.0, 77.1, 77.2, 77.3, 77.4, 77.5, 77.6, 77.7, 77.8, 77.9, 78.0], ARRAY[75.9, 76.0, 76.1, 76.2, 76.3, 76.4, 76.5, 76.6, 76.7, 76.8, 76.9, 77.0, 77.1, 77.2, 77.3, 77.4, 77.5, 77.6, 77.7, 77.8, 77.9], ARRAY[76.1, 76.2, 76.3, 76.4, 76.5, 76.6, 76.7, 76.8, 76.9, 77.0, 77.1, 77.2, 77.3, 77.4, 77.5, 77.6, 77.7, 77.8, 77.9, 78.0, 78.1]),
('2023-10-01 00:00:00', 1, 'temperature', 'min', 77.1, FALSE, FALSE, 0, ARRAY[77.1, 77.2, 77.3, 77.4, 77.5, 77.6, 77.7, 77.8, 77.9, 78.0, 78.1, 78.2, 78.3, 78.4, 78.5, 78.6, 78.7, 78.8, 78.9, 79.0, 79.1], ARRAY[77.0, 77.1, 77.2, 77.3, 77.4, 77.5, 77.6, 77.7, 77.8, 77.9, 78.0, 78.1, 78.2, 78.3, 78.4, 78.5, 78.6, 78.7, 78.8, 78.9, 79.0], ARRAY[77.2, 77.3, 77.4, 77.5, 77.6, 77.7, 77.8, 77.9, 78.0, 78.1, 78.2, 78.3, 78.4, 78.5, 78.6, 78.7, 78.8, 78.9, 79.0, 79.1, 79.2]),
('2023-10-01 00:00:00', 2, 'offline_time', 'avg', 5.5, FALSE, FALSE, 0, ARRAY[5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5], ARRAY[5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4], ARRAY[5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6]),
('2023-10-01 00:00:00', 2, 'offline_time', 'sum', 6.0, FALSE, FALSE, 0, ARRAY[6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8.0], ARRAY[5.9, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9], ARRAY[6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8.0, 8.1]);

-- Populate seasonalities table
INSERT INTO seasonalities (timestamp, MachineID, kpi, aggregation_type, selected_f)
VALUES
    ('2024-12-01 08:00:00', 1, 'temperature', 'avg', 5),
    ('2024-12-01 09:00:00', 2, 'offline_time', 'min', 3),
    ('2024-12-01 10:00:00', 3, 'cycles', 'sum', 4),
    ('2024-12-01 11:00:00', 4, 'cost', 'max', 2),
    ('2024-12-02 08:00:00', 1, 'offline_time', 'avg', 6),
    ('2024-12-02 09:00:00', 2, 'temperature', 'min', 2),
    ('2024-12-02 10:00:00', 3, 'cost', 'sum', 7),
    ('2024-12-02 11:00:00', 4, 'cycles', 'max', 8);

-- Populate thresholds table
INSERT INTO thresholds (timestamp, MachineID, kpi, aggregation_type, min_threshold, max_threshold)
VALUES
    ('2024-12-01 08:00:00', 1, 'temperature', 'avg', 20.0, 25.0),
    ('2024-12-01 09:00:00', 2, 'offline_time', 'min', 5.0, 10.0),
    ('2024-12-01 10:00:00', 3, 'cycles', 'sum', 100.0, 200.0),
    ('2024-12-01 11:00:00', 4, 'cost', 'max', 300.0, 400.0),
    ('2024-12-02 08:00:00', 1, 'offline_time', 'avg', 4.0, 8.0),
    ('2024-12-02 09:00:00', 2, 'temperature', 'min', 15.0, 20.0),
    ('2024-12-02 10:00:00', 3, 'cost', 'sum', 50.0, 150.0),
    ('2024-12-02 11:00:00', 4, 'cycles', 'max', 250.0, 350.0);
