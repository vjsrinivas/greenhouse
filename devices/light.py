from devices.relay import RelayModule

class LightBulb:
    def __init__(self, device_name: str, relay_module):
        self.__relay__ = relay_module
        self.__dev__ = device_name
        self.__state__ = False # False -> off; True -> on

    def start_light(self):
        self.__relay__[self.__dev__].on()

    def stop_light(self):
        self.__relay__[self.__dev__].off()

    def __call__(self, state:bool):
        # Toggle states:
        if state:
            self.start_light()
        else:
            self.stop_light()
        self.__state__ = state

    @property
    def readable(self):
        return True
