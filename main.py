import json
import os
import sys
from queue import Queue
from types import SimpleNamespace
from typing import *
from datetime import datetime

from loguru import logger

# Device imports:
from devices.sensor.camera import *
from devices.instrument.light import *
from devices.relay import *
from devices.sensor.sht31d import *
from devices.sensor.soil import *
from devices.sensor.tsl2591 import *
from devices.instrument.water import *
from devices.instrument.fan import *

# scheduling imports:
from scheduler import *
from utils import emoji

def initialize_from_config(config_file: str, return_relay_module:bool=False):
    config = json.load(open(config_file, "r"))
    device_tree = {}
    sensor_tree = {}
    instrument_tree = {}
    log_path = config["log_path"]

    # Create relay module list:
    relay_info = config["relay_module"]
    relay_modules = RelayModule(relay_info)

    for dev in config["devices"].keys():
        # Switch case to generate the correct object:
        device = config["devices"][dev]
        dev_type = device["type"]
        scheduler_obj = None
        device_type = None
        connections = config["devices"][dev].get("connections", None) 

        if dev_type == "light_sensor":
            i2c_addr = device["multiplex_idx"]
            interval_sec = device["interval_sec"]
            device_obj = LightSensor(i2c_addr, dev, use_multi_channel=True)
            scheduler_obj = SensorScheduler(interval_sec=interval_sec)
            device_type = "sensor"

        elif dev_type == "temperature_sensor":
            i2c_addr = device["multiplex_idx"]
            interval_sec = device["interval_sec"]
            device_obj = TemperatureSensor(i2c_addr, dev, use_multi_channel=True)
            scheduler_obj = SensorScheduler(interval_sec=interval_sec)
            device_type = "sensor"

        elif dev_type == "soil_sensor":
            i2c_addr = device["multiplex_idx"]
            interval_sec = device["interval_sec"]
            device_obj = SoilSensor(i2c_addr, dev, use_multi_channel=True)
            scheduler_obj = SensorScheduler(interval_sec=interval_sec)
            device_type = "sensor"

        elif dev_type == "light":
            device_obj = LightBulb(dev, relay_modules)
            device_type = "device"
            scheduler_obj = DeviceScheduler()

        elif dev_type == "water":
            device_obj = WaterPump(dev, relay_modules)
            device_type = "device"
            scheduler_obj = DeviceScheduler()

        elif dev_type == "camera":
            camera_id = device["usb_id"]
            save_path = device["save_path"]
            interval_sec = device["interval_sec"]
            device_obj = GC0307(camera_id, dev, GC0307_RESOLUTION.RES640P, save_path)
            device_type = "sensor"
            scheduler_obj = SensorScheduler(interval_sec=interval_sec)
        
        elif dev_type == "fan":
            device_obj = Fan(dev, relay_modules)
            device_type = "device"
            scheduler_obj = DeviceScheduler()

        else:
            raise ValueError("Type {} is not detected!".format(dev_type))

        
        device_tree_obj = SimpleNamespace(
            device=device_obj,
            type=dev_type,
            connections=connections,
            scheduler=scheduler_obj,
        )

        if device_type == "sensor":
            sensor_tree[dev] = device_tree_obj
        else:
            instrument_tree[dev] = device_tree_obj

    if return_relay_module:
        return sensor_tree, instrument_tree, relay_modules, log_path
    else:
        return sensor_tree, instrument_tree, log_path

def generate_status_log(devices, i_queue:Queue=None) -> str:
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
    
    # Optional printing of active queue (only used for when we're in the main loop)
    if i_queue is not None:
        if i_queue.qsize() > 0:
            status_log += "Active Queue Items:\n"
        
        for i in range(i_queue.qsize()):
            dname, dconn, dsensor = i_queue.queue[i]
            status_log += "\t ({}) to {}\n".format(dname, dconn)

    return status_log

def parse_arg():
    parser = ArgumentParser()
    parser.add_argument("--config", type=str, default="config.json", required=False, help="Path to device configuration file")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arg()
    CONFIG_FILE = args.config
    LOG_PATH = CONFIG_FILE["log_path"]
    sensor_tree, instrument_tree, log_path = initialize_from_config(CONFIG_FILE)
    interaction_queue = Queue()

    # 1. Declare device status
    logger.info("Sensor Status:")
    status_str = generate_status_log(sensor_tree, interaction_queue)
    logger.info(status_str)

    logger.info("Instrument Status:")
    status_str = generate_status_log(instrument_tree, interaction_queue)
    logger.info(status_str)

    # 1. Logging variables:
    datetime_format = "%Y-%m-%d_%H-%M-%S"
    start_timestamp = datetime.now()
    os.makedirs(log_path, exist_ok=True)

    # 1a. Setup sensor logging system
    log_paths = {}
    for _dev in sensor_tree.keys():
        if sensor_tree[_dev].type != "camera":
            log_paths[_dev] = os.path.join(log_path, "{}_{}.txt".format(_dev, start_timestamp.strftime(datetime_format))) 
    log_objects = {_dev:None for _dev in log_paths.keys()}

    for _dev in log_paths.keys():
        _path = log_paths[_dev]
        logger.info("Writing sensor object of {} to log path {}".format(_dev, _path))
        _header_csv = "timestamp"
        device_obj = sensor_tree[_dev].device
        for _key in device_obj.keys:
            _header_csv += ",{}".format(_key)
        _header_csv += "\n"
        log_objects[_dev] = open(_path, "w") 
        log_objects[_dev].write(_header_csv) 

    # 1b. Setup instrument (single-run) logging:
    run_path = os.path.join(LOG_PATH, "run_{}.txt".format(start_timestamp.strftime(datetime_format)))
    logger.info("Writing run file to {}".format(run_path))
    run_log = open(run_path, "w")
    run_log.write("type, state\n")

    # 2. Main loop:
    while True:
        run_log.write("heartbeat, off\n")

        # Loop through each sensor and take a measurement of the greenhouse environment:
        for device_name, device in sensor_tree.items(): 
            device_obj = device.device
            scheduler = device.scheduler

            if scheduler.can_schedule():
                sensor_timestamp = datetime.now()

                # Read sensor data
                sensor_dict = device_obj()
                
                # log sensor data:
                if device.type != "camera":
                    _header_csv = sensor_timestamp.strftime(datetime_format)
                    for _key in sensor_dict.keys():
                        _header_csv += ",{}".format(sensor_dict[_key])
                    _header_csv += "\n"
                    log_objects[device_name].flush()

                logger.debug("Placing {} into queue".format(device_name))
                interaction_queue.put((device_name, device.connections, sensor_dict, sensor_timestamp))

        """
        Once we've cycled through each applicable sensor reading,
        check each instrument and determine if it should change state
        """ 
        while interaction_queue.qsize() > 0:
            # Unload and unpack data object from queue:
            dname, dconn, dsensor, dtimestamp = interaction_queue.get()
            print(dname, dconn, dsensor)
            
            if len(dconn) > 0:
                for _conn in dconn:
                    _dev = instrument_tree[_conn]
                    scheduler:DeviceScheduler = _dev.scheduler

                    # Can the instrument be changed?
                    if scheduler.can_schedule(dsensor):
                        # What is the new state that the instrument should be in? 
                        new_state = scheduler.change(dsensor)
                        scheduler.update_budget(new_state, dtimestamp) # Update the internal scheduling budget (ex: light budget)
                        _dev.device(state=new_state)
                    else:
                        logger.warning("{} scheduler is not ready to be polled!")

        time.sleep(1) # tick every 1 second
