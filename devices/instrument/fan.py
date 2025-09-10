import os
import sys

class Fan:
    def __init__(self, device_name: str, relay_module, duration=10):
        self.__relay__ = relay_module
        self.__dev__ = device_name
        self.__state__ = False # False -> off; True -> on
        self.__duration__ = duration

    def start_fan(self):
        self.__relay__[self.__dev__].on()

    def stop_fan(self):
        self.__relay__[self.__dev__].off()

    @property
    def keys(self):
        return ["state"]

    def __call__(self, state:bool=None):
        # Toggle states:
        if state is None:
            state = not self.__state__

        if state:
            self.start_fan()
        else:
            self.stop_fan()
        self.__state__ = state
        return {"state": state}

    @property
    def state(self):
        return self.__state__

    @property
    def readable(self):
        return True
