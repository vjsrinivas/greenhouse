import os
import sys
from threading import Thread
from loguru import logger
import time

class Fan:
    def __init__(self, device_name: str, relay_module, duration=10):
        self.__relay__ = relay_module
        self.__dev__ = device_name
        self.__state__ = False # False -> off; True -> on
        self.__duration__ = duration
        self.thread_start = False
        self.active_thread = None

    def start_fan(self):
        self.__relay__[self.__dev__].on()

    def stop_fan(self):
        self.__relay__[self.__dev__].off()

    def __thread_function__(self, duration):
        start_time = time.time()
        active_duration = time.time() - start_time
        
        self.start_fan()
        while active_duration < self.__duration__:
            active_duration = time.time() - start_time
        self.stop_fan()
        self.thread_start=False
        return active_duration

    @property
    def keys(self):
        return ["state"]

    def trigger(self, state:bool=None):
        if state is None:
            # Start thread function!
            if not self.thread_start:
                # start pump thread; otherwise, skip with warning
                self.active_thread = Thread(target=self.__thread_function__, args=(self.__duration__,))
                self.active_thread.start()
                self.thread_start = True
            else:
                logger.warning("Fan thread is still active")
            
            return {"state": True}
        else:
            if not self.thread_start:
                if state:
                    self.start_fan()
                else:
                    self.stop_fan()
                self.__state__ = state
            else:
                logger.warning("Fan thread is still active")

            return {"state": state}

    @property
    def state(self):
        return self.__state__

    @property
    def readable(self):
        return True
