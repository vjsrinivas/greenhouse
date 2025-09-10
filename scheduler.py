import os
import sys
import time
import operator
from abc import ABC, abstractmethod
from datetime import datetime
from loguru import logger

"""
Types of scheduling:
    - Timer (in seconds)
    - Sensor (reading and triggering from devices; global timings too)
"""


# Base class:
class Scheduler(ABC):
    def __init__(self, interval_sec):
        self.last_interval = time.time()
        self.interval_sec = interval_sec

    @abstractmethod
    def can_schedule(self) -> bool:
        pass


# Generic sensor scheduler:
class SensorScheduler(Scheduler):
    def __init__(self, interval_sec=10):
        super().__init__(interval_sec)

    def can_schedule(self) -> bool:
        current_time = time.time()
        delta = current_time - self.last_interval
        if delta >= self.interval_sec:
            self.last_interval = current_time
            return True
        else:
            return False


# Generic device scheduler:
class DeviceScheduler(Scheduler):
    def __init__(self, sensor_threshold=100, interval_sec=10, comparison="less", budget_sec:float=1000, accumulation_state:bool=True):
        super().__init__(interval_sec)
        self.sensor_threshold = sensor_threshold
        self.comparison = comparison
        self.budget = budget_sec
        self.current_budget = 0.0
        self.last_state_change = None # Undefined last state change
        self.accumulation_state = accumulation_state

        if self.comparison == "less":
            self.op = operator.lt
        elif self.comparison == "greater":
            self.op = operator.gt
        elif self.comparison == "equal":
            self.op = operator.eq
        else:
            raise ValueError(
                "{} is not a recognized comparison state".format(self.comparison)
            )

    def can_schedule(self) -> bool:
        current_time = time.time()
        delta = current_time - self.last_interval
        if delta >= self.interval_sec:
            self.last_interval = current_time
            return True
        else:
            return False

    def change(self, sensor_input: float) -> bool:
        # sensor conditions:
        if self.op(self.sensor_threshold, sensor_input) and self.budget >= self.current_budget:
            return True
        else:
            return False

    def update_budget(self, state, sensor_timestamp:datetime):
        if self.accumulation_state == state:
            current_timestamp = datetime.now()
            minute_duration = sensor_timestamp-current_timestamp
            self.current_budget += (minute_duration.seconds/60)
            logger.info("Current budget: {} | Budget: {}".format(self.current_budget, self.budget))
