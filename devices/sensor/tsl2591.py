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
    """Aggregates multiple TSL2591 light sensors into a single logical sensor.

    This class averages the readings (lux, infrared, and full spectrum) from multiple
    LightSensor instances, optionally supporting TCA9548A multiplexer channels.

    Args:
        addresses (List[int]): List of I²C addresses (or multiplexer channels) for each sensor.
        descriptions (List[str]): List of human-readable descriptions for each sensor.
        skip_on_fail (bool, optional): Whether to ignore initialization failures. Defaults to True.
        use_multi_channel (bool, optional): Whether to use a TCA9548A multiplexer. Defaults to False.

    Example:
        >>> fused_sensor = FusedLightSensor([1, 2], ["Light #1", "Light #2"], use_multi_channel=True)
        >>> fused_sensor.lux
        432.5
        >>> fused_sensor()
        {'lux': 432.5, 'infrared': 120.3, 'spectrum': 550.1}
    """

    def __init__(self, addresses:List[int], descriptions:List[str], skip_on_fail=True, use_multi_channel=False):
        self.addresses = addresses # direct i2c connection
        self.descriptions = descriptions
        self.sensors = [LightSensor(addresses[i], descriptions[i], skip_on_fail, use_multi_channel) for i in range(len(addresses))]

    @property
    def readable(self):
        """Checks if at least one sensor is readable.

        Returns:
            bool: True if at least one sensor is active, False otherwise.
        """
        return any([sensor.readable for sensor in self.sensors])

    @property
    def lux(self):
        """Average lux reading across all sensors.

        Returns:
            float: Mean lux value.
        """
        return float(np.mean( [sensor.lux for sensor in self.sensors] ))

    @property
    def infrared(self):
        """Average infrared reading across all sensors.

        Returns:
            float: Mean infrared value.
        """
        return float(np.mean( [sensor.infrared for sensor in self.sensors] ))

    @property
    def spectrum(self):
        """Average full spectrum reading across all sensors.

        Returns:
            float: Mean full spectrum value.
        """
        return float(np.mean( [sensor.spectrum for sensor in self.sensors] ))

    @property
    def keys(self):
        """Returns the sensor data keys.

        Returns:
            List[str]: ['lux', 'infrared', 'spectrum']
        """
        return ["lux", "infrared", "spectrum"]

    def __call__(self):
        """Returns all averaged sensor readings as a dictionary.

        Returns:
            Dict[str, float]: {'lux': ..., 'infrared': ..., 'spectrum': ...}
        """
        return {"lux": self.lux, "infrared": self.infrared, "spectrum": self.spectrum}


class LightSensor:
    """Wrapper class for a single TSL2591 light sensor.

    Handles I²C connection, optional TCA9548A multiplexer support, and retries on initialization.

    Args:
        address (int): I²C address or multiplexer channel.
        description (str): Human-readable name for the sensor.
        skip_on_fail (bool, optional): Whether to skip initialization errors. Defaults to True.
        use_multi_channel (bool, optional): Whether to use a TCA9548A multiplexer. Defaults to False.

    Raises:
        Exception: If sensor initialization fails after multiple attempts and `skip_on_fail` is False.

    Example:
        >>> sensor = LightSensor(address=1, description="Light #1", use_multi_channel=True)
        >>> sensor.lux
        432.5
        >>> sensor()
        {'lux': 432.5, 'infrared': 120.3, 'spectrum': 550.1}
    """

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
        """Connects to the TSL2591 sensor over I²C.

        Supports direct I²C or via TCA9548A multiplexer.

        Raises:
            Exception: If connection fails and `skip_on_fail` is False.
        """
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
        """Checks if the sensor is readable.

        Returns:
            bool: True if the sensor is active, False if I²C connection failed.
        """
        return not self._i2c_fail

    @property
    def lux(self):
        """Current lux reading from the sensor.

        Returns:
            float: Lux value.
        """
        return self.tsl2591.lux

    @property
    def infrared(self):
        """Current infrared reading from the sensor.

        Returns:
            float: Infrared value.
        """
        return self.tsl2591.infrared

    @property
    def spectrum(self):
        """Current full spectrum reading from the sensor.

        Returns:
            float: Full spectrum value.
        """
        return self.tsl2591.full_spectrum

    def __init_probe__(self, probe_attempts=5):
        """Performs multiple read attempts to verify sensor is operational.

        Raises:
            Exception: Last exception encountered if all probe attempts fail.
        """
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
        """Returns the sensor data keys.

        Returns:
            List[str]: ['lux', 'infrared', 'spectrum']
        """
        return ["lux", "infrared", "spectrum"]

    def __call__(self):
        """Returns sensor readings as a dictionary.

        Returns:
            Dict[str, float]: {'lux': ..., 'infrared': ..., 'spectrum': ...}
        """
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

