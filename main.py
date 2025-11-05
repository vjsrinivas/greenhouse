import json
import os
import sys
from queue import Queue
from types import SimpleNamespace
from typing import *
from datetime import datetime
from argparse import ArgumentParser

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

# database logging:
from devices.database import DatabaseHandler, LogRecord, ImageRecord

# file manager:
from devices.file_manager import exec_manager
from multiprocessing import Process


def initialize_from_config(
    config_file: str, return_relay_module: bool = False, fake_data=False
):
    config = json.load(open(config_file, "r"))
    device_tree = {}
    sensor_tree = {}
    instrument_tree = {}
    light_sensors = []  # For fused sensor approach
    log_path = config["log_path"]
    budgets = config["budgets"]

    # Create relay module list:
    relay_info = config["relay_module"]
    relay_modules = RelayModule(relay_info, fake_data=fake_data)

    for dev in config["devices"].keys():
        # Switch case to generate the correct object:
        device = config["devices"][dev]
        dev_type = device["type"]
        scheduler_obj = None
        device_type = None
        limiter_key = None
        connections = config["devices"][dev].get("connections", None)

        if dev_type == "light_sensor":
            i2c_addr = device["multiplex_idx"]
            interval_sec = device["interval_sec"]
            light_sensors.append(
                [i2c_addr, dev, interval_sec, connections, limiter_key]
            )

        elif dev_type == "temperature_sensor":
            i2c_addr = device["multiplex_idx"]
            interval_sec = device["interval_sec"]
            device_obj = TemperatureSensor(
                i2c_addr,
                dev,
                use_multi_channel=True,
                temp_unit="fahrenheit",
                fake_data=fake_data,
            )
            scheduler_obj = SensorScheduler(interval_sec=interval_sec)
            device_type = "sensor"

        # TODO: Isn't implemented; would affect water pump
        elif dev_type == "soil_sensor":
            i2c_addr = device["multiplex_idx"]
            interval_sec = device["interval_sec"]
            device_obj = SoilSensor(
                i2c_addr, dev, use_multi_channel=True, fake_data=fake_data
            )
            scheduler_obj = SensorScheduler(interval_sec=interval_sec)
            device_type = "sensor"

        elif dev_type == "light":
            device_obj = LightBulb(dev, relay_modules, fake_data=fake_data)
            device_type = "device"
            limiters = device["sensor_keys"]
            limiter_key = "lux"  # TODO: make this multiple limits; have to make DeviceScheduler accept multiple thresholds
            scheduler_obj = DeviceScheduler(
                sensor_threshold=limiters[limiter_key],
                interval_sec=10,
                comparison="greater",
                budget_struct=budgets[dev],
                accumulation_state=True,
            )

        elif dev_type == "water":
            device_type = "device"
            duration_sec = device["duration"]
            interval_sec = device["interval_sec"]
            device_obj = WaterPump(
                dev, relay_modules, period=duration_sec, fake_data=fake_data
            )
            scheduler_obj = DeviceScheduler(
                sensor_threshold=0,
                interval_sec=interval_sec,
                comparison="equal",
                budget_struct={"seconds": 1e100},
                accumulation_state=True,
            )

        elif dev_type == "camera":
            camera_id = device["usb_id"]
            save_path = device["save_path"]
            interval_sec = device["interval_sec"]
            device_obj = GC0307(
                camera_id,
                dev,
                GC0307_RESOLUTION.RES640P,
                save_path,
                fake_data=fake_data,
            )
            device_type = "sensor"
            scheduler_obj = SensorScheduler(interval_sec=interval_sec)

        elif dev_type == "fan":
            device_type = "device"
            limiters = device["sensor_keys"]
            limiter_key = "temperature"  # TODO: make this multiple limits; have to make DeviceScheduler accept multiple thresholds
            duration_sec = device["duration"]
            interval_sec = device["interval_sec"]

            device_obj = Fan(
                dev, relay_modules, duration=duration_sec, fake_data=fake_data
            )

            # Two schedules - one for an interval and one when the temperature gets too hot
            iterative_scheduler_obj = DeviceScheduler(
                sensor_threshold=0,
                interval_sec=interval_sec,
                comparison="equal",
                budget_struct={"seconds": 1e100},
                accumulation_state=True,
            )
            scheduler_obj = DeviceScheduler(
                sensor_threshold=limiters[limiter_key],
                interval_sec=interval_sec,
                comparison="less",
                budget_struct={"seconds": 86400},
                accumulation_state=True,
            )
        else:
            raise ValueError("Type {} is not detected!".format(dev_type))

        if not dev_type in ["light_sensor"]:
            if dev_type == "fan":
                device_tree_obj = SimpleNamespace(
                    device=device_obj,
                    type=dev_type,
                    connections=connections,
                    scheduler=[
                        scheduler_obj,
                        iterative_scheduler_obj,
                    ],  # TODO: break into its own class
                    run_alone=True,
                    limiter_key=limiter_key,
                )
            else:
                device_tree_obj = SimpleNamespace(
                    device=device_obj,
                    type=dev_type,
                    connections=connections,
                    scheduler=[scheduler_obj],
                    run_alone=False,
                    limiter_key=limiter_key,
                )

        # Some exceptions to consider:
        if dev_type == "water":
            device_tree_obj.run_alone = True

        if device_type == "sensor":
            sensor_tree[dev] = device_tree_obj
        else:
            instrument_tree[dev] = device_tree_obj

    if len(light_sensors) > 0:
        addrs = [ls[0] for ls in light_sensors]
        descs = [ls[1] for ls in light_sensors]
        connections = list(set([ls[3][0] for ls in light_sensors]))
        name = "+".join(descs)
        avg_interval_sec = sum([ls[2] for ls in light_sensors]) / (len(light_sensors))
        device_obj = FusedLightSensor(
            addrs, descs, use_multi_channel=True, fake_data=fake_data
        )
        scheduler_obj = SensorScheduler(interval_sec=avg_interval_sec)
        device_type = "sensor"
        device_tree_obj = SimpleNamespace(
            device=device_obj,
            type="light_sensor",
            connections=connections,
            scheduler=[scheduler_obj],
            run_alone=False,
            limiter_key=limiter_key,
        )
        sensor_tree[name] = device_tree_obj

    if return_relay_module:
        return sensor_tree, instrument_tree, relay_modules, log_path
    else:
        return sensor_tree, instrument_tree, log_path


def generate_status_log(devices, i_queue: Queue = None) -> str:
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
    parser.add_argument(
        "--fake-data",
        action="store_true",
        required=False,
        default=False,
        help="Flag to ",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        required=False,
        help="Path to device configuration file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arg()
    CONFIG_FILE = args.config
    sensor_tree, instrument_tree, log_path = initialize_from_config(
        CONFIG_FILE, fake_data=args.fake_data
    )
    interaction_queue = Queue()
    logging_iteration = 1
    loop_iteration = 0

    # 1. Declare device status
    logger.info("Sensor Status:")
    status_str = generate_status_log(sensor_tree, interaction_queue)
    logger.info(status_str)

    logger.info("Instrument Status:")
    status_str = generate_status_log(instrument_tree, interaction_queue)
    logger.info(status_str)

    # 1a. Initialize database variables for logging:
    datetime_format = "%Y-%m-%d_%H-%M-%S"
    start_timestamp = datetime.now()

    # 1a. Setup sensor logging system
    db_handler = DatabaseHandler("./logs/internal.db")
    file_manager_process = Process(target=exec_manager, args=('./logs', db_handler), daemon=True)
    file_manager_process.start()

    # 2. Main loop:
    while True:
        db_handler.heartbeat()

        # Loop through each sensor and take a measurement of the greenhouse environment:
        for device_name, device in sensor_tree.items():
            device_obj = device.device
            scheduler_list = device.scheduler

            for scheduler in scheduler_list:
                if scheduler.can_schedule():
                    sensor_timestamp = datetime.now()

                    # Read sensor data
                    sensor_dict = device_obj()

                    # log sensor data:
                    if device.type != "camera":
                        record = LogRecord(
                            name=device_name,
                            level="INFO",
                            message="{} sensor reading".format(device_name),
                            metadata=json.dumps(sensor_dict),
                        )
                        db_handler.log(record)

                        logger.debug("Placing {} into queue".format(device_name))
                        interaction_queue.put(
                            (
                                device_name,
                                device.connections,
                                sensor_dict,
                                sensor_timestamp,
                            )
                        )
                    else:
                        image_record = ImageRecord(
                            name=sensor_dict["name"], path=sensor_dict["save_path"]
                        )
                        db_handler.record_image(image_record)

        """
        Once we've cycled through each applicable sensor reading,
        check each instrument and determine if it should change state
        """
        while interaction_queue.qsize() > 0:
            # Unload and unpack data object from queue:
            dname, dconn, dsensor, dtimestamp = interaction_queue.get()

            if len(dconn) > 0:
                for _conn in dconn:
                    _dev = instrument_tree[_conn]
                    scheduler_list: List[DeviceScheduler] = _dev.scheduler

                    # TODO: This is a workaround; break scheduler list into Namespace objects
                    if len(scheduler_list) > 1:
                        scheduler_list = [
                            scheduler_list[0]
                        ]  # Get just the sensor-based scheduler

                    for scheduler in scheduler_list:
                        # Can the instrument be changed?
                        if scheduler.can_schedule():
                            # What is the new state that the instrument should be in?
                            new_state = scheduler.change(dsensor[_dev.limiter_key])
                            scheduler.update_budget(
                                new_state, dtimestamp
                            )  # Update the internal scheduling budget (ex: light budget)
                            _dev.device.trigger(state=new_state)

                            record = LogRecord(
                                name=dname,
                                level="INFO",
                                message="{} instrument state change".format(dname),
                                metadata=json.dumps(
                                    {"connection": _conn, "state": new_state}
                                ),
                            )
                            db_handler.log(record)
                        else:
                            # if loop_iteration % logging_iteration == 0 or _dev.run_alone:
                            logger.warning(
                                "{} scheduler is not ready to be polled!".format(_conn)
                            )

        # Run through any instrument scheduler that is on an iterative timer (no sensor attached)
        for instrument_name, instrument in instrument_tree.items():
            if instrument.run_alone:
                scheduler_list = instrument.scheduler
                # TODO: This is a workaround; break scheduler list into Namespace objects
                if len(scheduler_list) > 1:
                    scheduler_list = [
                        scheduler_list[1]
                    ]  # Get just the iterative-based scheduler

                for scheduler in scheduler_list:
                    if scheduler.can_schedule():
                        # What is the new state that the instrument should be in?
                        new_state = scheduler.change(0)
                        scheduler.update_budget(
                            new_state, datetime.now()
                        )  # Update the internal scheduling budget (ex: light budget)

                        if instrument_name in ["fan_1", "fan_2"]:
                            instrument.device.trigger(state=None)
                        else:
                            instrument.device.trigger(state=new_state)

                        record = LogRecord(
                            name=instrument_name,
                            level="INFO",
                            message="{} interval instrument state change".format(
                                instrument_name
                            ),
                            metadata=json.dumps(
                                {"connection": None, "state": new_state}
                            ),
                        )
                        db_handler.log(record)
                    else:
                        if loop_iteration % logging_iteration == 0:
                            logger.warning(
                                "(Iterative) {} scheduler is not ready to be polled!".format(
                                    instrument_name
                                )
                            )

        time.sleep(1)  # tick every 1 second

        loop_iteration += 1
        if loop_iteration >= 1e10:
            loop_iteration = 0  # prevent any possible overflow
