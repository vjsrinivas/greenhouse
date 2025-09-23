import os
import sys
import time
import operator
from abc import ABC, abstractmethod
from datetime import datetime
from loguru import logger
from typing import *

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
    def __init__(self, sensor_threshold=100, interval_sec=10, comparison="less", budget_struct:Optional[Dict]=None, accumulation_state:bool=True):
        super().__init__(interval_sec)
        self.sensor_threshold = sensor_threshold
        self.comparison = comparison
        self.budget = budget_struct
        self.budget_sec = self.budget["seconds"]
        budget_time_format = "%I:%M:%S %p"
        self.budget_start, self.budget_end = None, None
        if "time_start" in self.budget:
            if self.budget["time_start"] != "N/A":
                self.budget_start = datetime.strptime(self.budget["time_start"], budget_time_format)
            
        if "time_end" in self.budget:
            if self.budget["time_end"] != "N/A":
                self.budget_end = datetime.strptime(self.budget["time_end"], budget_time_format)

        if (self.budget_start is None or self.budget_end is None) and not (self.budget_start is None and self.budget_end is None):
            raise ValueError("budget_start and budget_end must both be defined or not at all!")

        self.current_budget = 0.0
        self.last_state_change = None # Undefined last state change
        self.accumulation_state = accumulation_state

        if self.comparison == "less":
            self.op = operator.lt
        elif self.comparison == "greater":
            self.op = operator.gt
        elif self.comparison == "equal":
            self.op = operator.eq
        elif self.comparison == "not_equal":
            self.op = operator.ne
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
        current_timestamp = datetime.now()
        can_run = True
        if self.budget_start is not None:
            if not self.in_timerange(self.budget_start, self.budget_end, current_timestamp):
                can_run = False
                logger.warning("Scheduler's change function is not in time range: {}".format(self.budget_start.time(), self.budget_end.time()))
                
        if self.op(self.sensor_threshold, sensor_input) and self.budget_sec >= self.current_budget and can_run:
            return True
        else:
            return False

    def in_timerange(self, start: datetime, end: datetime, check: datetime) -> bool:
        """Return True if check's time is within [start, end], ignoring date."""
        s, e, c = start.time(), end.time(), check.time()
        if s <= e:  # Normal case (same day)
            return s <= c <= e
        else:       # Range crosses midnight
            return c >= s or c <= e
    
    def update_budget(self, state, sensor_timestamp:datetime) -> None:
        current_timestamp = datetime.now()
        if current_timestamp.day != sensor_timestamp.day:
            logger.info("New day detected; reset budget and skip this iteration")
            self.current_budget = 0
            return None

        can_run = True
        if self.budget_start is not None:
            if not self.in_timerange(self.budget_start, self.budget_end, current_timestamp):
                can_run = False
                logger.warning("Scheduler update_budget is not in time range: {}".format(self.budget_start.time(), self.budget_end.time()))

        if can_run:
            self.current_budget += self.interval_sec
        
        if self.accumulation_state == state and can_run:
            minute_duration = current_timestamp-sensor_timestamp
            self.current_budget += minute_duration.seconds
            logger.info("Current budget: {} | Budget: {}".format(self.current_budget, self.budget))
            return None

    @property
    def next_poll_time(self):
        current_time = datetime.now()
        next_poll = self.last_interval + self.interval_sec
        dt = datetime.fromtimestamp(next_poll)
        next_date_poll = dt.strftime("%-I:%M:%S %p %-m/%-d/%Y")
        delta = (current_time-next_date_poll)
        return delta.seconds
