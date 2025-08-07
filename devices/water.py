from devices.relay import RelayModule
from threading import Thread
import time
from loguru import logger

class WaterPump:
    def __init__(self, device_name: str, relay_module):
        self.__relay__ = relay_module
        self.__dev__ = device_name
        self.__state__ = False
        self.period_spacing = 10
        self.period = 5

    def start_pump(self):
        self.__relay__[self.__dev__].on()

    def stop_pump(self):
        self.__relay__[self.__dev__].off()

    def pump(self, period_spacing_ms=10, period_sec=5):
        t1 = time.time()
        self.start_pump()

        while True:
            if period_spacing_ms != -1:
                self.stop_pump()
                time.sleep(period_spacing_ms/1000.0)
                self.start_pump()
            t2 = time.time()
            if t2-t1 > period_sec:
                break

        self.stop_pump()
        stop_duration = time.time() - t1
        return stop_duration

    @property
    def keys(self):
        return ["pump_time", "duration"]

    def __call__(self, state:bool=None):
        if state is None:
            state = not self.__state__

        if state:
            # Pump blocks main thread:
            _duration = self.pump(self.period_spacing, self.period)
        else:
            _duration = 0.0

        self.__state__ = state
        return {"pump_time":time.time() , "duration": _duration}

    @property
    def readable(self):
        return True
