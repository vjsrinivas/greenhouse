import adafruit_sht31d as sht31d
import board
from typing import *
import busio
from loguru import logger

class TemperatureSensor:
    def __init__(self, address:int, description:str, temp_unit:Literal["celsius", "fahrenheit"]="celsius", skip_on_fail=True):
        # Check if given temperature unit is valid
        self.__sunits__ = ["celsius", "fahrenheit"]
        if not (temp_unit in self.__sunits__):
            raise ValueError("{} is not a valid choice for temperature unit. Supported units: {}, {}".format(temp_unit, *self.__sunits__))

        self.addr = address
        self.__desc__ = description
        self.temp_unit = temp_unit
        self.skip_on_fail = skip_on_fail
        self._i2c_fail = False

        # Connect to temp sensor:
        self.__connect__()
        
        # Push off bad first data:
        if not self._i2c_fail:
            _first_temp = self.temperature
            _first_humd = self.relative_humidity
            logger.debug("Dumped first reading (temp: {} | rh: {})".format(_first_temp, _first_humd))

    def __connect__(self):
        try:
            logger.info("Connecting (SCL:{} | SDA:{} | Address: {})".format(board.SCL, board.SDA, self.addr))
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.sht31d = sht31d.SHT31D(self.i2c, address=self.addr)
        except Exception as e:
            self._i2c_fail = True
            logger.error(e)
            if not self.skip_on_fail:
                raise e 

    @property
    def temperature(self):
        if self.temp_unit == "celsius":
            return self.sht31d.temperature
        elif self.temp_unit == "fahrenheit":
            _temp = self.sht31d.temperature
            _f_temp = (_temp*1.8)+32
            return _f_temp
        else:
            raise ValueError("Unrecognized self.temp_unit: {}".format(self.temp_unit))

    @property
    def readable(self):
        return not self._i2c_fail

    @property
    def relative_humidity(self):
        return self.sht31d.relative_humidity

if __name__ == "__main__":
    temp_sensor = TemperatureSensor(address=0x44, description="Temperature Sensor #1", temp_unit="fahrenheit")
    while True:
        logger.info("Temperature: {} | {}".format(temp_sensor.temperature, temp_sensor.relative_humidity))
