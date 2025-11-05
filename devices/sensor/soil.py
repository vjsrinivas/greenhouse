from typing import *
import board
import busio
from loguru import logger
from adafruit_seesaw.seesaw import (
    Seesaw,
)  # Generic soil sensor that can be used for Adafruit STEMMA soil sensor
import adafruit_tca9548a
import random

class SoilSensor:
    """A class for interfacing with Adafruit STEMMA-compatible soil sensors (Seesaw).

    This class provides access to soil moisture and temperature readings over I²C.
    It supports both single-channel and multi-channel configurations (via TCA9548A multiplexer).

    Args:
        address (int): I²C address or channel index of the soil sensor.
        description (str): A descriptive name for the sensor instance.
        temp_unit (Literal["celsius", "fahrenheit"], optional): Unit for temperature readings. Defaults to `"celsius"`.
        skip_on_fail (bool, optional): Whether to skip sensor initialization errors instead of raising exceptions. Defaults to `True`.
        use_multi_channel (bool, optional): Whether to connect through a TCA9548A multiplexer. Defaults to `False`.

    Raises:
        ValueError: If an invalid temperature unit is provided.
        RuntimeError: If sensor initialization fails and `skip_on_fail` is `False`.

    Example:
        >>> from devices.soil_sensor import SoilSensor
        >>> sensor = SoilSensor(0x36, "garden_sensor_1")
        >>> print(sensor.moisture)
        542
        >>> print(sensor.temperature)
        23.4
    """

    def __init__(
        self,
        address: int,
        description: str,
        temp_unit: Literal["celsius", "fahrenheit"] = "celsius",
        skip_on_fail=True,
        use_multi_channel=False,
        fake_data=False
    ):
        """Initializes the soil sensor and establishes an I²C connection.

        Args:
            address (int): I²C address (e.g., `0x36`) or multiplexer channel number.
            description (str): A descriptive name for the sensor.
            temp_unit (Literal["celsius", "fahrenheit"], optional): Desired temperature unit. Defaults to `"celsius"`.
            skip_on_fail (bool, optional): Whether to suppress initialization errors. Defaults to `True`.
            use_multi_channel (bool, optional): Whether to use a TCA9548A multiplexer. Defaults to `False`.

        Raises:
            ValueError: If `temp_unit` is not `"celsius"` or `"fahrenheit"`.
            RuntimeError: If initialization fails and `skip_on_fail` is `False`.

        Example:
            >>> sensor = SoilSensor(2, "multi_channel_sensor", use_multi_channel=True)
        """

        # Check if given temperature unit is valid
        self.__sunits__ = ["celsius", "fahrenheit"]
        if not (temp_unit in self.__sunits__):
            raise ValueError(
                "{} is not a valid choice for temperature unit. Supported units: {}, {}".format(
                    temp_unit, *self.__sunits__
                )
            )
        self.temp_unit = temp_unit

        self.addr = address
        self.__desc__ = description
        self.skip_on_fail = skip_on_fail
        self._i2c_fail = False
        self.use_multi = use_multi_channel
        self.fake_data = fake_data

        # Connect to soil sensor:
        if not self.fake_data:
            self.__connect__()

    def __connect__(self):
        """Initializes the I²C interface and connects to the soil sensor.

        This method supports both direct and multi-channel (TCA9548A) connections.

        Raises:
            Exception: If connection fails and `skip_on_fail` is `False`.
        """
        
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.tca = adafruit_tca9548a.TCA9548A(self.i2c)
        self.stemma_obj = Seesaw(self.tca[self.addr])
        exit()

        try:
            logger.info(
                "Connecting (SCL:{} | SDA:{} | Address: {})".format(
                    board.SCL, board.SDA, self.addr
                )
            )
            self.i2c = busio.I2C(board.SCL, board.SDA)
            
            if self.use_multi:
                self.tca = adafruit_tca9548a.TCA9548A(self.i2c)
                self.stemma_obj = Seesaw(self.tca[self.addr])     
                exit()
            else:
                self.stemma_obj = Seesaw(self.i2c, addr=self.addr)
        
        except Exception as e:
            self._i2c_fail = True
            logger.error(e)
            if not self.skip_on_fail:
                raise e

    @property
    def readable(self):
        """Checks if the soil sensor is readable (I²C connection is healthy).

        Returns:
            bool: `True` if sensor is readable, otherwise `False`.

        Example:
            >>> if sensor.readable:
            ...     print("Sensor connected and active.")
        """
        if not self.fake_data:
            return True
        return not self._i2c_fail

    @property
    def moisture(self):
        """Reads the current soil moisture level.

        Returns:
            int: The moisture level as a raw sensor value (0–1023 range for most devices).

        Raises:
            RuntimeError: If the sensor is not connected or readable.

        Example:
            >>> print(sensor.moisture)
            512
        """
        if self.fake_data:
            return random.random()*100.0
        return self.stemma_obj.moisture_read()

    @property
    def temperature(self):
        """Reads the current temperature from the soil sensor.

        Returns:
            float: Temperature in Celsius or Fahrenheit depending on configuration.

        Raises:
            RuntimeError: If the sensor is not connected or readable.
            ValueError: If an unknown temperature unit is encountered.

        Example:
            >>> print(sensor.temperature)
            24.3
        """
        if self.fake_data:
            return random.random()*100.0

        temp = self.stemma_obj.get_temp()
        if self.temp_unit == "celsius":
            return temp
        elif self.temp_unit == "fahrenheit":
            _f_temp = (temp * 1.8) + 32
            return _f_temp
        else:
            raise ValueError("Unrecognized self.temp_unit: {}".format(self.temp_unit))


if __name__ == "__main__":
    import time

    #sensor = SoilSensor(0x36, "soil_sensor_1")
    sensor = SoilSensor(2, "soil_sensor_1", use_multi_channel=True)

    while True:
        print(sensor.moisture, sensor.temperature)
        time.sleep(1)
