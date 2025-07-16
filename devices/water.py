from devices.relay import RelayModule

class WaterPump:
    def __init__(self, device_name:str, relay_module):
        self.__relay__ = relay_module
        self.__dev__ = device_name

    def start_pump(self):
        self.__relay__[self.__dev__].on()        

    def stop_pump(self):
        self.__relay__[self.__dev__].off()

    @property
    def readable(self):
        return True
