import os
import sys
import busio
import board
from adafruit_tsl2591 import TSL2591
from loguru import logger
import adafruit_tca9548a
from typing import *
import numpy as np
import time

class FusedLightSensor:
    def __init__(self, addresses:List[int], descriptions:List[str], skip_on_fail=True, use_multi_channel=False):
        self.addresses = addresses # direct i2c connection
        self.descriptions = descriptions
        self.sensors = [LightSensor(addresses[i], descriptions[i], skip_on_fail, use_multi_channel) for i in range(len(addresses))]

    @property
    def readable(self):
        return any([sensor.readable for sensor in self.sensors])

    @property
    def lux(self):
        return float(np.mean( [sensor.lux for sensor in self.sensors] ))

    @property
    def infrared(self):
        return float(np.mean( [sensor.infrared for sensor in self.sensors] ))

    @property
    def spectrum(self):
        return float(np.mean( [sensor.spectrum for sensor in self.sensors] ))

    @property
    def keys(self):
        return ["lux", "infrared", "spectrum"]

    def __call__(self):
        return {"lux": self.lux, "infrared": self.infrared, "spectrum": self.spectrum}


class LightSensor:
    def __init__(self, address: int, description: str, skip_on_fail=True, use_multi_channel=False):
        self.addr = address # direct i2c connection
        self.use_multi = use_multi_channel
        self.name = description
        self.skip_on_fail = skip_on_fail
        self._i2c_fail = False

        # Connect to temp sensor:
        self.__connect__()
        self.__init_probe__()

    def __connect__(self):
        try:
            logger.info(
                "Connecting (SCL:{} | SDA:{} | Address: {})".format(
                    board.SCL, board.SDA, self.addr
                )
            )
            self.i2c = busio.I2C(board.SCL, board.SDA)
            
            if self.use_multi:
                self.tca = adafruit_tca9548a.TCA9548A(self.i2c)
                self.tsl2591 = TSL2591(self.tca[self.addr])
            else:
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

    def __init_probe__(self, probe_attempts=5):
        successes = 0
        last_exception = None
        for i in range(probe_attempts):
            try:
                _ = self.lux
                _ = self.infrared
                _ = self.spectrum
                successes += 1
                break
            except Exception as e:
                last_exception = e

        if successes == 0:
            raise last_exception
        else:
            return None
    
    @property
    def keys(self):
        return ["lux", "infrared", "spectrum"]

    def __call__(self):
        return {"lux": self.lux, "infrared": self.infrared, "spectrum": self.spectrum}


if __name__ == "__main__":
    fused_sensor = FusedLightSensor(addresses=[1,2], descriptions=["Light #1", "Light #2"], use_multi_channel=True)
    #sensor = LightSensor(address=0x29, description="Light Sensor #1")
    sensor1 = LightSensor(address=1, description="Light Sensor #1", use_multi_channel=True)
    sensor2 = LightSensor(address=2, description="Light Sensor #2", use_multi_channel=True)
    while True:
        print(fused_sensor())
        print(sensor1(), sensor2())
        #logger.info("{} Lux: {}".format(sensor1.name, sensor1.lux))
        #logger.info("{} Lux: {}".format(sensor2.name, sensor2.lux))
        time.sleep(2)

