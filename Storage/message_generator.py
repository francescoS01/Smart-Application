"""
This module contains classes and functions for generating sensor measurements with constraints.
"""

import random
from enum import Enum
from typing import List, Dict, Optional


class Measurement(Enum):
    """Enum representing different types of measurements."""

    WORKING_TIME = "working_time"  # Working time measurement
    IDLE_TIME = "idle_time"  # Idle time measurement
    OFFLINE_TIME = "offline_time"  # Offline time measurement
    CONSUMPTION = "consumption"  # Consumption measurement
    POWER = "power"  # Power measurement
    COST = "cost"  # Cost measurement
    COST_IDLE = "cost_idle"  # Cost during idle time measurement
    COST_WORKING = "cost_working"  # Cost during working time measurement
    CONSUMPTION_WORKING = "consumption_working"  # Consumption during working time measurement
    CONSUMPTION_IDLE = "consumption_idle"  # Consumption during idle time measurement
    CYCLES = "cycles"  # Number of cycles measurement
    GOOD_CYCLES = "good_cycles"  # Number of good cycles measurement
    BAD_CYCLES = "bad_cycles"  # Number of bad cycles measurement
    AVERAGE_CYCLE_TIME = "average_cycle_time"  # Average cycle time measurement
    TEMPERATURE = "temperature"  # Temperature measurement
    ACCELERATION_X = "acceleration_x"  # Acceleration in the X direction
    ACCELERATION_Y = "acceleration_y"  # Acceleration in the Y direction
    ACCELERATION_Z = "acceleration_z"  # Acceleration in the Z direction


class ConstraintType(Enum):
    """Enum representing the type of constraints for measurements."""

    POSITIVE = "positive"
    BOTH = "both"


CONSTRAINTS = {
    Measurement.WORKING_TIME: ConstraintType.POSITIVE,
    Measurement.IDLE_TIME: ConstraintType.POSITIVE,
    Measurement.OFFLINE_TIME: ConstraintType.POSITIVE,
    Measurement.CONSUMPTION: ConstraintType.POSITIVE,
    Measurement.POWER: ConstraintType.POSITIVE,
    Measurement.COST: ConstraintType.POSITIVE,
    Measurement.COST_IDLE: ConstraintType.POSITIVE,
    Measurement.COST_WORKING: ConstraintType.POSITIVE,
    Measurement.CONSUMPTION_WORKING: ConstraintType.POSITIVE,
    Measurement.CONSUMPTION_IDLE: ConstraintType.POSITIVE,
    Measurement.CYCLES: ConstraintType.POSITIVE,
    Measurement.GOOD_CYCLES: ConstraintType.POSITIVE,
    Measurement.BAD_CYCLES: ConstraintType.POSITIVE,
    Measurement.AVERAGE_CYCLE_TIME: ConstraintType.POSITIVE,
    Measurement.TEMPERATURE: ConstraintType.POSITIVE,
    Measurement.ACCELERATION_X: ConstraintType.BOTH,
    Measurement.ACCELERATION_Y: ConstraintType.BOTH,
    Measurement.ACCELERATION_Z: ConstraintType.BOTH,
}


class SensorMeasurement:
    """
    Class to handle sensor measurements with constraints on their values.

    Attributes:
        measurements (List[str]): List of measurement types.
        means (Dict[str, float]): Dictionary of mean values for each measurement.
        variances (Dict[str, float]): Dictionary of variance values for each measurement.
    """

    def __init__(
        self,
        measurements: List[str],
        means: Optional[Dict[str, float]] = None,
        variances: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize the SensorMeasurement object.

        Args:
            measurements (List[str]): List of measurement types.
            means (Optional[Dict[str, float]]): Dictionary of mean values for each measurement.
            variances (Optional[Dict[str, float]]): Dictionary of variance values for each measurement.

        Raises:
            ValueError: If measurements list is empty or contains invalid measurement types.
            NotImplementedError: If a constraint type is not implemented.
        """
        if not measurements:
            raise ValueError("Measurements list cannot be empty.")

        self.measurements: List[str] = measurements
        self.means: Dict[str, float] = {}
        self.variances: Dict[str, float] = {}

        for measurement in measurements:
            try:
                Measurement(measurement)
            except ValueError:
                raise ValueError(
                    f"Measurement {measurement} is not a valid Measurement type."
                )

            constraint = CONSTRAINTS.get(Measurement(measurement))
            if constraint == ConstraintType.POSITIVE:
                self.means[measurement] = abs(means.get(measurement, 1)) if means else 1
                self.variances[measurement] = (
                    abs(variances.get(measurement, 1)) if variances else 1
                )
            elif constraint == ConstraintType.BOTH:
                self.means[measurement] = means.get(measurement, 0) if means else 0
                self.variances[measurement] = (
                    abs(variances.get(measurement, 1)) if variances else 1
                )
            else:
                raise NotImplementedError(
                    f"Constraint type for measurement {measurement} is not implemented."
                )

    def set_mean(self, measurement: str, mean: float) -> None:
        """
        Set the mean value for a specific measurement.

        Args:
            measurement (str): The measurement type.
            mean (float): The mean value to set.

        Raises:
            ValueError: If the measurement is not valid.
        """
        if measurement in self.measurements:
            if CONSTRAINTS[Measurement(measurement)] == ConstraintType.POSITIVE:
                self.means[measurement] = abs(mean)
            else:
                self.means[measurement] = mean
        else:
            raise ValueError(f"Measurement {measurement} is not valid.")

    def set_variance(self, measurement: str, variance: float) -> None:
        """
        Set the variance value for a specific measurement.

        Args:
            measurement (str): The measurement type.
            variance (float): The variance value to set.

        Raises:
            ValueError: If the measurement is not valid or variance is negative.
        """
        if variance <= 0:
            raise ValueError("Variance cannot be negative.")
        if measurement in self.measurements:
            self.variances[measurement] = variance
        else:
            raise ValueError(f"Measurement {measurement} is not valid.")

    def generate_random_measurement(self) -> Dict[str, float]:
        """
        Generate random measurement values based on the mean and variance.

        Returns:
            Dict[str, float]: Dictionary of generated measurement values.

        Raises:
            NotImplementedError: If a constraint type is not implemented.
        """
        measurement_data: Dict[str, float] = {}
        for measurement in self.measurements:
            mean = self.means.get(measurement, 0)
            variance = self.variances.get(measurement, 1)
            value = random.gauss(mean, variance)
            if CONSTRAINTS[Measurement(measurement)] == ConstraintType.POSITIVE:
                value = abs(value)
            elif CONSTRAINTS[Measurement(measurement)] != ConstraintType.BOTH:
                raise NotImplementedError(
                    f"Constraint type for measurement {measurement} is not implemented."
                )
            measurement_data[measurement] = value
        return measurement_data
