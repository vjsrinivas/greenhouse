import os
import sys
from loguru import logger
from typing import *
import json
from utils import emoji

# Device imports:
from devices.camera import *
from devices.relay import *
from devices.sht31d import *
from devices.tsl2591 import *
from devices.water import *
from devices.light import *
from devices.soil import *

def initialize_from_config(config_file:str):
    config = json.load(open(config_file, "r"))
    device_tree = {}

    # Create relay module list:
    relay_info = config["relay_module"]
    relay_modules = RelayModule(relay_info)

    for dev in config["devices"].keys():
        print(dev)
        input()

        # Switch case to generate the correct object:
        device = config["devices"][dev] 
        dev_type = device["type"]
        if dev_type == "light_sensor":
            i2c_addr = int(device["i2c_address"], 16)
            device_obj = LightSensor(i2c_addr, dev) 
        elif dev_type == "temperature_sensor":
            i2c_addr = int(device["i2c_address"], 16)
            device_obj = TemperatureSensor(i2c_addr, dev) 
        elif dev_type == "soil_sensor":
            i2c_addr = int(device["i2c_address"], 16)
            device_obj = SoilSensor(i2c_addr, dev)
        elif dev_type == "light":
            device_obj = LightBulb(dev, relay_modules)
        elif dev_type == "water":
            device_obj = WaterPump(dev, relay_modules)
        elif dev_type == "camera":
            camera_id = device["usb_id"]
            device_obj = GC0307(camera_id, dev, GC0307_RESOLUTION.RES640P) 
        else:
            raise ValueError("Type {} is not detected!".format(dev_type))
        
        device_tree[dev] = device_obj

    return device_tree

if __name__ == "__main__":
    CONFIG_FILE = "config.json"
    devices = initialize_from_config(CONFIG_FILE)
    
    for device_name, device_obj in devices.items():
        if device_obj.readable:
            status = emoji.success
        else:
            status = emoji.warning
        logger.info("{} - {}".format(device_name, status))
