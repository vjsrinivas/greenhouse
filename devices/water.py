from devices.relay import RelayModule

class WaterPump:
    def __init__(self, device_name:str, relay_module):
        self.__relay__ = relay_module

    def start_pump(self):
        self.__relay__.on()        

    def stop_pump(self):
        self.__relay__.off()
