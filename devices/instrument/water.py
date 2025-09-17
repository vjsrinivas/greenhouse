from devices.relay import RelayModule
from threading import Thread
import time
from loguru import logger

class WaterPump:
    def __init__(self, device_name: str, relay_module):
        self.__relay__ = relay_module
        self.__dev__ = device_name
        self.__state__ = False
        self.period_spacing = 10 # ms
        self.period = 5 # seconds
        
        self.thread_duration = 0.0
        self.thread_start = False
        self.active_thread = None

    def start_pump(self):
        self.__relay__[self.__dev__].on()

    def stop_pump(self):
        self.__relay__[self.__dev__].off()

    def __thread_function__(self, period_spacing_ms=10, period_sec=5):
        t1 = time.time()
        
        # NOTE: Enable once water bucket is filled with water
        # self.start_pump()

        while True:
            if period_spacing_ms != -1:
                # NOTE: Enable once water bucket is filled with water
                # self.stop_pump()

                time.sleep(period_spacing_ms/1000.0)
                
                # NOTE: Enable once water bucket is filled with water
                # self.start_pump()
            t2 = time.time()
            if t2-t1 > period_sec:
                break

        # NOTE: Enable once water bucket is filled with water
        # self.stop_pump()
        stop_duration = time.time() - t1
        self.thread_active = False
        self.thread_duration = stop_duration
        logger.info("Water pump thread exiting after {} seconds".format(self.thread_duration))

    def trigger(self, state):
        if not self.thread_start:
            # start pump thread; otherwise, skip with warning
            self.active_thread = Thread(target=self.__thread_function__, args=(self.period_spacing, self.period))
            self.active_thread.start()
            self.thread_active = True
        else:
            logger.warning("Water pump thread is still active")

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
    def state(self):
        return self.__state__

    @property
    def readable(self):
        return True
