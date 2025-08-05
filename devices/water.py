from devices.relay import RelayModule
from threading import Thread
import time
from loguru import logger

class WaterPump:
    def __init__(self, device_name: str, relay_module):
        self.__relay__ = relay_module
        self.__dev__ = device_name
        self.__active__ = False

    def start_pump(self):
        self.__relay__[self.__dev__].on()

    def stop_pump(self):
        self.__relay__[self.__dev__].off()

    def pump(self, period_spacing_ms=10, period_sec=5):
        _thread = Thread(target=self.__pump_thread__, args=(period_spacing_ms, period_sec))
        _thread.start()
        return _thread

    def __pump_thread__(self, period_spacing_ms, period_sec) -> int:
        self.__active__ = True
        try:
            t1 = time.time()
            while time.time() - t1 < period_sec:
                self.start_pump()
                time.sleep(period_spacing_ms/1000)
                self.stop_pump()
            self.stop_pump()
            self.__active__ = False
            return 0
        except Exception as e:
            logger.error(e)
            self.__active__ = False
            return -1    

    def __call__(self, state):
        if not self.__active__:
            self.pump()

    @property
    def readable(self):
        return True
