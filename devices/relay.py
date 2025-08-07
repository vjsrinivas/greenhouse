import os
import sys

from gpiozero import LED, OutputDevice
import time
from typing import *

try:
    from utils import emoji
except ImportError:
    pass

class RelayModule:
    def __init__(self, pin_mapping: Dict):
        """
        pin_mapping (Dict) -> "device_str": pin_int
        """
        self.__pin__ = pin_mapping
        self.relays = {}
        for dev, pin in self.__pin__.items():
            self.relays[dev] = OutputDevice(pin, active_high=False, initial_value=False)

    def __device_chk__(self, device_name: str):
        assert device_name in self.__pin__, "{} is not a key in pin mapping!".format(
            device_name
        )

    def on(self, device_name: str):
        self.__device_chk__(device_name)
        self.relays[device_name].on()

    def off(self, device_name: str):
        self.__device_chk__(device_name)
        self.relays[device_name].off()

    def __repr__(self):
        _str = "Relay Status:\n"
        for dev, pin in self.__pin__.items():
            _relay = self.relays[dev]
            if _relay.value == 1:
                _value_str = "On"
                _value = emoji.good
            else:
                _value_str = "Off"
                _value = emoji.bad
            # _str += "{} - {}\n".format(dev, _value_str)
            _str += "{:^15} - {} ({})\n".format(dev, _value, _value_str)
        return _str

    def __getitem__(self, key:str):
        return self.relays[key]


if __name__ == "__main__":
    import time
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--pin", required=False, default=17)
    args = parser.parse_args()

    # Test relaying:
    PIN = args.pin
    relay = OutputDevice(PIN, active_high=False, initial_value=False)
    #relay2 = OutputDevice(27, active_high=False, initial_value=True)
    print(relay.value)
    input()

    while True:
        relay.on()
        #relay2.off()
        print(relay.value)
        time.sleep(1)
        relay.off()
        #relay2.on()
        print(relay.value)
        time.sleep(1)
    # test_relay = RelayModule({"water_pump": 17})
    # test_relay.on("water_pump")
