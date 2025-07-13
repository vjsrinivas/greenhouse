import os
import sys

from gpiozero import LED, OutputDevice
import time
from typing import *
from utils import emoji

class RelayModule:
    def __init__(self, pin_mapping:Dict):
        """
        pin_mapping (Dict) -> "device_str": pin_int
        """
        self.__pin__ = pin_mapping
        self.relays = []
        for dev, pin in self.__pin__.items():
            self.relays.append( OutputDevice(pin, active_high=False, initial_value=False) )
        
    def __device_chk__(self, device_name:str):
        assert device_name in self.__pin__, "{} is not a key in pin mapping!".format(device_name)

    def on(self, device_name:str):
        self.__device_chk__()
        self.relays[device_name].on()

    def off(self, device_name:str):
        self.__device_chk__()
        self.relays[device_name].off()

    def __repr__(self):
        _str = ""
        for dev, pin in self.__pin__.items():
            if pin.value == 1:
                _value_str = "On"
                _value = emoji.good
            else:
                _value_str = "Off"
                _value = emoji.bad
            _str += "{} - {} ({})".format(dev, _value, _value_str)
        return _str

if __name__ == "__main__":
    # Test relaying:
    pass
