"""
Unit tests for the SensorMeasurement class and its methods.

These tests cover the initialization, setting means and variances, generating random measurements,
and handling of constraints and invalid inputs for the SensorMeasurement class.
"""

import pytest
from Storage.message_generator import SensorMeasurement, Measurement, CONSTRAINTS


def test_sensor_measurement_initialization():
    measurements = [Measurement.WORKING_TIME.value, Measurement.IDLE_TIME.value]
    means = {Measurement.WORKING_TIME.value: 10, Measurement.IDLE_TIME.value: 5}
    variances = {Measurement.WORKING_TIME.value: 2, Measurement.IDLE_TIME.value: 1}
    sensor = SensorMeasurement(measurements, means, variances)

    assert sensor.means[Measurement.WORKING_TIME.value] == 10
    assert sensor.means[Measurement.IDLE_TIME.value] == 5
    assert sensor.variances[Measurement.WORKING_TIME.value] == 2
    assert sensor.variances[Measurement.IDLE_TIME.value] == 1


def test_set_mean():
    measurements = [Measurement.WORKING_TIME.value]
    sensor = SensorMeasurement(measurements)
    sensor.set_mean(Measurement.WORKING_TIME.value, 15)

    assert sensor.means[Measurement.WORKING_TIME.value] == 15


def test_set_variance():
    measurements = [Measurement.WORKING_TIME.value]
    sensor = SensorMeasurement(measurements)
    sensor.set_variance(Measurement.WORKING_TIME.value, 3)

    assert sensor.variances[Measurement.WORKING_TIME.value] == 3


def test_generate_random_measurement():
    measurements = [Measurement.WORKING_TIME.value]
    means = {Measurement.WORKING_TIME.value: 10}
    variances = {Measurement.WORKING_TIME.value: 2}
    sensor = SensorMeasurement(measurements, means, variances)

    random_measurement = sensor.generate_random_measurement()

    assert Measurement.WORKING_TIME.value in random_measurement
    assert (
        random_measurement[Measurement.WORKING_TIME.value] >= 0
    )  # Since it's positive constraint


def test_invalid_measurement():
    measurements = [Measurement.WORKING_TIME.value]
    sensor = SensorMeasurement(measurements)

    with pytest.raises(ValueError):
        sensor.set_mean("invalid_measurement", 10)

    with pytest.raises(ValueError):
        sensor.set_variance("invalid_measurement", 2)


def test_empty_measurements():
    with pytest.raises(ValueError):
        SensorMeasurement([])


def test_invalid_measurement_type():
    measurements = ["invalid_measurement"]
    with pytest.raises(ValueError):
        SensorMeasurement(measurements)


def test_negative_variance():
    measurements = [Measurement.WORKING_TIME.value]
    means = {Measurement.WORKING_TIME.value: 10}
    variances = {Measurement.WORKING_TIME.value: -2}
    sensor = SensorMeasurement(measurements, means, variances)

    assert (
        sensor.variances[Measurement.WORKING_TIME.value] == 2
    )  # Should be converted to positive


def test_unsupported_constraint_type():
    measurements = [Measurement.WORKING_TIME.value]
    means = {Measurement.WORKING_TIME.value: 10}
    variances = {Measurement.WORKING_TIME.value: 2}

    # Temporarily add an unsupported constraint type
    original_constraints = CONSTRAINTS[Measurement.WORKING_TIME]
    CONSTRAINTS[Measurement.WORKING_TIME] = "unsupported"

    with pytest.raises(NotImplementedError):
        SensorMeasurement(measurements, means, variances)

    # Restore the original constraint
    CONSTRAINTS[Measurement.WORKING_TIME] = original_constraints


def test_set_mean_valid_measurement():
    measurements = [Measurement.WORKING_TIME.value]
    sensor = SensorMeasurement(measurements)
    sensor.set_mean(Measurement.WORKING_TIME.value, 10.0)
    assert sensor.means[Measurement.WORKING_TIME.value] == 10.0


def test_set_mean_invalid_measurement():
    measurements = [Measurement.WORKING_TIME.value]
    sensor = SensorMeasurement(measurements)
    with pytest.raises(
        ValueError, match="Measurement invalid_measurement is not valid."
    ):
        sensor.set_mean("invalid_measurement", 10.0)


def test_set_mean_edge_case_zero():
    measurements = [Measurement.WORKING_TIME.value]
    sensor = SensorMeasurement(measurements)
    sensor.set_mean(Measurement.WORKING_TIME.value, 0.0)
    assert sensor.means[Measurement.WORKING_TIME.value] == 0.0


def test_set_mean_edge_case_negative():
    measurements = [Measurement.ACCELERATION_X.value]
    sensor = SensorMeasurement(measurements)
    sensor.set_mean(Measurement.ACCELERATION_X.value, -5.0)
    assert sensor.means[Measurement.ACCELERATION_X.value] == -5.0


def test_set_variance_valid_measurement():
    measurements = [Measurement.WORKING_TIME.value]
    sensor = SensorMeasurement(measurements)
    sensor.set_variance(Measurement.WORKING_TIME.value, 2.0)
    assert sensor.variances[Measurement.WORKING_TIME.value] == 2.0

def test_set_variance_invalid_measurement():
    measurements = [Measurement.WORKING_TIME.value]
    sensor = SensorMeasurement(measurements)
    with pytest.raises(ValueError, match="Measurement invalid_measurement is not valid."):
        sensor.set_variance("invalid_measurement", 2.0)

def test_set_variance_edge_case_zero():
    measurements = [Measurement.WORKING_TIME.value]
    sensor = SensorMeasurement(measurements)
    with pytest.raises(ValueError, match="Variance cannot be negative."):
        sensor.set_variance(Measurement.WORKING_TIME.value, 0.0)

def test_set_variance_edge_case_negative():
    measurements = [Measurement.WORKING_TIME.value]
    sensor = SensorMeasurement(measurements)
    with pytest.raises(ValueError, match="Variance cannot be negative."):
        sensor.set_variance(Measurement.WORKING_TIME.value, -3.0)

def test_constructor_positive_constraint():
    measurements = [Measurement.WORKING_TIME.value]
    means = {Measurement.WORKING_TIME.value: -10}
    variances = {Measurement.WORKING_TIME.value: -2}
    sensor = SensorMeasurement(measurements, means, variances)

    assert sensor.means[Measurement.WORKING_TIME.value] == 10  # Should be positive
    assert sensor.variances[Measurement.WORKING_TIME.value] == 2  # Should be positive

def test_constructor_both_constraint():
    measurements = [Measurement.ACCELERATION_X.value]
    means = {Measurement.ACCELERATION_X.value: -10}
    variances = {Measurement.ACCELERATION_X.value: -2}
    sensor = SensorMeasurement(measurements, means, variances)

    assert sensor.means[Measurement.ACCELERATION_X.value] == -10  # Should remain negative
    assert sensor.variances[Measurement.ACCELERATION_X.value] == 2  # Should be positive

def test_constructor_default_values_both_constraint():
    measurements = [Measurement.ACCELERATION_X.value]
    sensor = SensorMeasurement(measurements)

    assert sensor.means[Measurement.ACCELERATION_X.value] == 0  # Default mean
    assert sensor.variances[Measurement.ACCELERATION_X.value] == 1  # Default variance


def test_constructor_default_values_positive_constraint():
    measurements = [Measurement.WORKING_TIME.value]
    sensor = SensorMeasurement(measurements)

    assert sensor.means[Measurement.WORKING_TIME.value] == 1  # Default mean for positive constraint
    assert sensor.variances[Measurement.WORKING_TIME.value] == 1  # Default variance

def test_set_mean_respects_positive_constraint():
    measurements = [Measurement.WORKING_TIME.value]
    sensor = SensorMeasurement(measurements)
    sensor.set_mean(Measurement.WORKING_TIME.value, -10.0)
    assert sensor.means[Measurement.WORKING_TIME.value] == 10.0  # Should be positive

def test_set_mean_respects_both_constraint():
    measurements = [Measurement.ACCELERATION_X.value]
    sensor = SensorMeasurement(measurements)
    sensor.set_mean(Measurement.ACCELERATION_X.value, -10.0)
    assert sensor.means[Measurement.ACCELERATION_X.value] == -10.0  # Should remain negative
