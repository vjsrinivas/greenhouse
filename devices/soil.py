from typing import *
import board
import busio
from loguru import logger
from adafruit_seesaw.seesaw import Seesaw # Generic soil sensor that can be used for Adafruit STEMMA soil sensor

class SoilSensor:
    def __init__(self, address:int, description:str, temp_unit:Literal["celsius", "fahrenheit"]="celsius", skip_on_fail=True):
        # Check if given temperature unit is valid
        self.__sunits__ = ["celsius", "fahrenheit"]
        if not (temp_unit in self.__sunits__):
            raise ValueError("{} is not a valid choice for temperature unit. Supported units: {}, {}".format(temp_unit, *self.__sunits__))
        self.temp_unit = temp_unit

        self.addr = address
        self.__desc__ = description
        self.skip_on_fail = skip_on_fail
        self._i2c_fail = False
        
        # Connect to soil sensor:
        self.__connect__()

    def __connect__(self):
        try:
            logger.info("Connecting (SCL:{} | SDA:{} | Address: {})".format(board.SCL, board.SDA, self.addr))
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.stemma_obj = Seesaw(self.i2c, addr=self.addr)
        except Exception as e:
            self._i2c_fail = True
            logger.error(e)
            if not self.skip_on_fail:
                raise e 

    @property
    def readable(self):
        return not self._i2c_fail

    @property 
    def moisture(self):
        return self.stemma_obj.moisture_read()

    @property
    def temperature(self):
        temp = self.stemma_obj.get_temp()
        if self.temp_unit == "celsius":
            return temp
        elif self.temp_unit == "fahrenheit":
            _f_temp = (temp*1.8)+32
            return _f_temp
        else:
            raise ValueError("Unrecognized self.temp_unit: {}".format(self.temp_unit))

if __name__ == "__main__":
    import time
    sensor = SoilSensor(0x36, "soil_sensor_1")
    
    while True:
        print(sensor.moisture, sensor.temperature)
        time.sleep(1)
