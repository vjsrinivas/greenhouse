import adafruit_sht31d as sht31d
import board
from typing import *
import busio
from loguru import logger
import adafruit_tca9548a
import random

class TemperatureSensor:
    """
    Interface for an SHT31D temperature and humidity sensor.

    This class manages the connection to an SHT31D sensor over I2C, allowing
    temperature (in Celsius or Fahrenheit) and relative humidity readings.
    It also supports usage with a TCA9548A multiplexer for multi-channel setups.

    Args:
        address (int): The I2C address of the sensor or multiplexer channel.
        description (str): A user-defined description of the sensor.
        temp_unit (str, optional): Unit in which temperature values are reported.
            Must be either `"celsius"` or `"fahrenheit"`. Default is `"celsius"`.
        skip_on_fail (bool, optional): If True, sensor connection failures will not
            raise an exception. Default is True.
        use_multi_channel (bool, optional): If True, attempts connection through a
            TCA9548A multiplexer. Default is False.

    Raises:
        ValueError: If an unsupported temperature unit is provided.
        Exception: If connection fails and `skip_on_fail` is False.

    Example:
        >>> sensor = TemperatureSensor(address=0x44, description="Greenhouse sensor")
        >>> sensor.readable
        True
        >>> sensor.temperature
        22.5
        >>> sensor.relative_humidity
        45.3
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
        # Check if given temperature unit is valid
        self.__sunits__ = ["celsius", "fahrenheit"]
        if not (temp_unit in self.__sunits__):
            raise ValueError(
                "{} is not a valid choice for temperature unit. Supported units: {}, {}".format(
                    temp_unit, *self.__sunits__
                )
            )

        self.addr = address
        self.__desc__ = description
        self.temp_unit = temp_unit
        self.skip_on_fail = skip_on_fail
        self._i2c_fail = False
        self.use_multi = use_multi_channel
        self.fake_data = fake_data

        # Connect to temp sensor:
        if not self.fake_data:
            self.__connect__()
            self.__init_probe__()
    
        # Push off bad first data:
        if not self._i2c_fail:
            _first_temp = self.temperature
            _first_humd = self.relative_humidity
            logger.debug(
                "Dumped first reading (temp: {} | rh: {})".format(
                    _first_temp, _first_humd
                )
            )

    def __connect__(self):
        """
        Establish I2C connection with the sensor.

        If `use_multi` is True, connects via a TCA9548A multiplexer channel.
        Otherwise, connects directly to the I2C bus.

        Raises:
            Exception: Re-raised if `skip_on_fail` is False and connection fails.
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
                self.sht31d = sht31d.SHT31D(self.tca[self.addr])
            else:
                self.sht31d = sht31d.SHT31D(self.i2c, address=self.addr)
        
        except Exception as e:
            self._i2c_fail = True
            logger.error(e)
            if not self.skip_on_fail:
                raise e

    @property
    def temperature(self):
        """
        Current temperature reading from the sensor.

        Returns:
            float: Temperature value in Celsius or Fahrenheit depending on `temp_unit`.

        Raises:
            ValueError: If an unsupported unit is set for `temp_unit`.

        Example:
            >>> sensor = TemperatureSensor(0x44, "Test sensor")
            >>> sensor.temperature
            21.7
        """
        if self.fake_data:
            return random.random()*100.0

        if self.temp_unit == "celsius":
            return self.sht31d.temperature
        elif self.temp_unit == "fahrenheit":
            _temp = self.sht31d.temperature
            _f_temp = (_temp * 1.8) + 32
            return _f_temp
        else:
            raise ValueError("Unrecognized self.temp_unit: {}".format(self.temp_unit))

    @property
    def readable(self):
        """
        Whether the sensor is successfully readable.

        Returns:
            bool: True if sensor is working, False if initialization failed.

        Example:
            >>> sensor = TemperatureSensor(0x44, "Test sensor")
            >>> sensor.readable
            True
        """
        if self.fake_data:
            return True
        return not self._i2c_fail

    @property
    def relative_humidity(self):
        """
        Whether the sensor is successfully readable.

        Returns:
            bool: True if sensor is working, False if initialization failed.

        Example:
            >>> sensor = TemperatureSensor(0x44, "Test sensor")
            >>> sensor.readable
            True
        """
        if self.fake_data:
            return random.random()*100.0
        return self.sht31d.relative_humidity

    def __init_probe__(self, probe_attempts=5):
        """
        Whether the sensor is successfully readable.

        Returns:
            bool: True if sensor is working, False if initialization failed.

        Example:
            >>> sensor = TemperatureSensor(0x44, "Test sensor")
            >>> sensor.readable
            True
        """
        successes = 0
        last_exception = None
        for i in range(probe_attempts):
            try:
                _ = self.temperature
                _ = self.relative_humidity
                successes += 1
                break
            except Exception as e:
                last_exception = e

        if successes == 0:
            logger.error("Failed to probe SHT31D properly...")
            raise last_exception
        else:
            return None 

    @property
    def keys(self):
        """
        Data keys provided by the sensor.

        Returns:
            list of str: Always `["temperature", "relative_humidity"]`.

        Example:
            >>> sensor = TemperatureSensor(0x44, "Test sensor")
            >>> sensor.keys
            ['temperature', 'relative_humidity']
        """
        return ["temperature", "relative_humidity"]

    def __call__(self):
        """
        Get current sensor readings in dictionary format.

        Returns:
            dict: Dictionary with keys:
                - "temperature" (float): Temperature reading.
                - "relative_humidity" (float): Relative humidity reading.

        Example:
            >>> sensor = TemperatureSensor(0x44, "Test sensor")
            >>> sensor()
            {'temperature': 22.5, 'relative_humidity': 45.3}
        """
        return {"temperature": self.temperature, "relative_humidity": self.relative_humidity}

if __name__ == "__main__":
    import time
    """
    temp_sensor = TemperatureSensor(
        address=0x44, description="Temperature Sensor #1", temp_unit="fahrenheit"
    )
    """

    temp_sensor = TemperatureSensor(
        address=6, description="Temperature Sensor #1", temp_unit="fahrenheit", use_multi_channel=True
    )
    while True:
        print(temp_sensor())
        """
        logger.info(
            "Temperature: {} | {}".format(
                temp_sensor.temperature, temp_sensor.relative_humidity
            )
        )
        """
        time.sleep(1)
