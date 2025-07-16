import os
import sys
import time
import operator

"""
Types of scheduling:
    - Timer (in seconds)
    - Sensor (reading and triggering from devices; global timings too)
"""

# Base class:
class Scheduler:
    def __init__(self, interval_sec):
        self.last_interval = time.time()
        self.interval_sec = interval_sec

    def __call__(self) -> bool:
        raise NotImplementedError()

# Generic sensor scheduler:
class SensorScheduler(Scheduler):
    def __init__(self, interval_sec=10):
        super().__init__(interval_sec)

    def __call__(self) -> bool:
        current_time = time.time()
        delta = current_time - self.last_interval
        if delta >= self.interval_sec:
            self.last_interval = current_time
            return True
        else:
            return False

# Generic device scheduler:
class DeviceScheduler(Scheduler):
    def __init__(self, sensor_threshold=100, interval_sec=10, comparison="less"):
        super().__init__(interval_sec)
        self.sensor_threshold = sensor_threshold
        self.comparison = comparison

        if self.comparison == "less":
            self.op = operator.lt
        elif self.comparison == "greater":
            self.op = operator.gt

    def __call__(self, sensor_input:float) -> bool:
        current_time = time.time()
        delta = current_time - self.last_interval
        if delta >= self.interval_sec:
            self.last_interval = current_time
            
            # sensor conditions:
            if self.op(self.sensor, sensor_input):
                return True
            else:
                return False
        else:
            return False
