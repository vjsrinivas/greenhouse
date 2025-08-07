import json
import os
import sys
from queue import Queue
from types import SimpleNamespace
from typing import *
from datetime import datetime

from loguru import logger

# Device imports:
from devices.camera import *
from devices.light import *
from devices.relay import *
from devices.sht31d import *
from devices.soil import *
from devices.tsl2591 import *
from devices.water import *
from devices.fan import *

# scheduling imports:
from scheduler import *
from utils import emoji

def initialize_from_config(config_file: str):
    config = json.load(open(config_file, "r"))
    device_tree = {}
    log_path = config["log_path"]

    # Create relay module list:
    relay_info = config["relay_module"]
    relay_modules = RelayModule(relay_info)

    for dev in config["devices"].keys():
        # Switch case to generate the correct object:
        device = config["devices"][dev]
        dev_type = device["type"]
        scheduler_obj = None
        scheduler_type = None
        connections = config["devices"][dev].get("connections", None) 

        if dev_type == "light_sensor":
            i2c_addr = device["multiplex_idx"]
            interval_sec = device["interval"]
            device_obj = LightSensor(i2c_addr, dev, use_multi_channel=True)
            scheduler_obj = SensorScheduler(interval_sec=interval_sec)
            scheduler_type = "sensor"

        elif dev_type == "temperature_sensor":
            i2c_addr = device["multiplex_idx"]
            interval_sec = device["interval"]
            device_obj = TemperatureSensor(i2c_addr, dev, use_multi_channel=True)
            scheduler_obj = SensorScheduler(interval_sec=interval_sec)
            scheduler_type = "sensor"

        elif dev_type == "soil_sensor":
            i2c_addr = device["multiplex_idx"]
            interval_sec = device["interval"]
            device_obj = SoilSensor(i2c_addr, dev, use_multi_channel=True)
            scheduler_obj = SensorScheduler(interval_sec=interval_sec)
            scheduler_type = "sensor"

        elif dev_type == "light":
            device_obj = LightBulb(dev, relay_modules)
            scheduler_type = "device"
            scheduler_obj = DeviceScheduler()

        elif dev_type == "water":
            device_obj = WaterPump(dev, relay_modules)
            scheduler_type = "device"
            scheduler_obj = DeviceScheduler()

        elif dev_type == "camera":
            camera_id = device["usb_id"]
            save_path = device["save_path"]
            interval_sec = device["interval"]
            device_obj = GC0307(camera_id, dev, GC0307_RESOLUTION.RES640P, save_path)
            scheduler_type = "sensor"
            scheduler_obj = SensorScheduler(interval_sec=interval_sec)
        
        elif dev_type == "fan":
            device_obj = Fan(dev, relay_modules)
            scheduler_type = "device"
            scheduler_obj = DeviceScheduler()

        else:
            raise ValueError("Type {} is not detected!".format(dev_type))

        device_tree_obj = SimpleNamespace(
            device=device_obj,
            type=dev_type,
            connections=connections,
            scheduler=scheduler_obj,
            scheduler_type=scheduler_type,
        )
        device_tree[dev] = device_tree_obj

    return device_tree, relay_modules, log_path

def generate_status_log(devices, i_queue:Queue) -> str:
    status_log = "\n"
    for device_name, device in devices.items():
        device_obj, device_scheduler = device.device, device.scheduler
        if device_obj.readable:
            status = emoji.success
            status_str = "(Online)"
        else:
            status = emoji.warning
            status_str = "(Offline)"
        status_log += "\t{:<20} - {:<10} {}\n".format(device_name, status_str, status)
    status_log += "\n"
    
    if i_queue.qsize() > 0:
        status_log += "Active Queue Items:\n"
    
    for i in range(i_queue.qsize()):
        dname, dconn, dsensor = i_queue.queue[i]
        status_log += "\t ({}) to {}\n".format(dname, dconn)

    return status_log

if __name__ == "__main__":
    CONFIG_FILE = "config.json"
    devices, relays, log_path = initialize_from_config(CONFIG_FILE)
    interaction_queue = Queue()

    # 1. Declare device status
    status_str = generate_status_log(devices, interaction_queue)
    logger.info(status_str)

    # 1a. Setup sensor logging system
    datetime_format = "%Y-%m-%d_%H-%M-%S"
    start_timestamp = datetime.now()
    os.makedirs(log_path, exist_ok=True)
    
    log_paths = {}
    for _dev in devices.keys():
        if devices[_dev].type != "camera":
            log_paths[_dev] = os.path.join(log_path, "{}_{}.txt".format(_dev, start_timestamp.strftime(datetime_format))) 
    log_objects = {_dev:None for _dev in log_paths.keys()}

    for _dev in log_paths.keys():
        _path = log_paths[_dev]
        logger.info("Writing device object of {} to log path {}".format(_dev, _path))
        _header_csv = "timestamp"
        device_obj = devices[_dev].device
        for _key in device_obj.keys:
            _header_csv += ",{}".format(_key)
        _header_csv += "\n"
        log_objects[_dev] = open(_path, "w") 
        log_objects[_dev].write(_header_csv) 

    # 2. Main loop:
    while True:
        for device_name, device in devices.items(): 
            if device.scheduler_type == "sensor":
                device_obj = device.device
                device_scheduler = device.scheduler
                if device_scheduler():
                    sensor_timestamp = datetime.now()
                    sensor_dict = device_obj() # TODO: Replace with sensor reading
                    
                    # log sensor data:
                    if device.type != "camera":
                        _header_csv = sensor_timestamp.strftime(datetime_format)
                        for _key in sensor_dict.keys():
                            _header_csv += ",{}".format(sensor_dict[_key])
                        _header_csv += "\n"
                        log_objects[device_name].flush()

                    logger.debug("Placing {} into queue".format(device_name))
                    interaction_queue.put((device_name, device.connections, sensor_dict))
        
        while interaction_queue.qsize() > 0:
            dname, dconn, dsensor = interaction_queue.get()
            print(dname, dconn, dsensor)
            
            if len(dconn) > 0:
                for _conn in dconn:
                    _dev = devices[_conn]
                    print(dsensor)
                    exit()
                    if _dev.scheduler(dsensor):
                        # TODO: set device's primary property to active state
                        _dev.device(state=True)
                    else:
                        # TODO: reset device back to default state
                        _dev.device(state=False)

        time.sleep(1) # tick every 1 second
