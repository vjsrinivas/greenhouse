import os
import sys
from loguru import logger
from typing import *
import json
from utils import emoji

# Device imports:
from device.camera import *
from device.relay import *
from device.sht31d import *
from device.tsl2591 import *
from device.water import *
from device.soil import *

def initialize_from_config(config_file:str):
    config = json.load(open(config_file, "r"))
    device_tree = {}
    for dev in config["devices"].keys():
        device_tree[dev] = None
        
        # Switch case to generate the correct object:
        dev_type = dev["type"]
        if dev_type == "light_sensor":
            device_obj = LightSensor() 
        elif dev_type == "temperature_sensor":
            device_obj = TemperatureSensor() 
        elif dev_type == "soil_sensor":
            device_obj = SoilSensor()
        elif dev_type == "light":
            device_obj = Lights()
        elif dev_type == "water":
            device_obj = WaterPump()
        elif dev_type == "camera":
            device_obj = 
        else:
            raise ValueError("Type {} is not detected!".format(dev_type))

    return device_tree

if __name__ == "__main__":
    devices = initialize_from_config("config.json")
    
    for device in devices:
        if device.readable:
            status = emoji.success
        else:
            status = emoji.warning
        logger.info("{} - {}".format(device.name, status))
