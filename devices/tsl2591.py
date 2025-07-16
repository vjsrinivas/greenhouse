import os
import sys
import busio
import board
from adafruit_tsl2591 import TSL2591
from loguru import logger

class LightSensor:
    def __init__(self, address:int, description:str, skip_on_fail=True):
        self.addr = address
        self.__desc__ = description
        self.skip_on_fail = skip_on_fail
        self._i2c_fail = False

        # Connect to temp sensor:
        self.__connect__()

    def __connect__(self):
        try:
            logger.info("Connecting (SCL:{} | SDA:{} | Address: {})".format(board.SCL, board.SDA, self.addr))
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.tsl2591 = TSL2591(self.i2c, address=self.addr)
        except Exception as e:
            self._i2c_fail = True
            logger.error(e)
            if not self.skip_on_fail:
                raise e 
    @property
    def readable(self):
        return not self._i2c_fail

    @property
    def lux(self):
        return self.tsl2591.lux

    @property
    def infrared(self):
        return self.tsl2591.infrared

    @property
    def spectrum(self):
        return self.tsl2591.full_spectrum


if __name__ == "__main__":
    sensor = LightSensor(address=0x29, description="Light Sensor #1")
    while True:
        logger.info("Lux: {}".format(sensor.lux))
