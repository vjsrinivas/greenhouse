# Code Documentation

## Overall Structure

This documentation will breakdown the high-level software architecture defined in [STRUCTURE](STRUCTURE.md) into the following subitems:
    
* Configuration Structure
* Sensor Interfacing
* Relay Interfacing
* Scheduling Tasks
* Main Loop
* API Reference

## Configuration Structure

A configuration file is used to do the following:
* Define connection details to sensors and instruments
* To determine the frequency of a sensor reading or instrument action
* Which sensor should feed into what instrument
* Meta-data related to data storage

In this project, the configuration file is by default `config.json`, and the json structure is composed in the following structure:

| Level          | Purpose                                         |
|----------------|------------------------------------------------|
| `log_path`     | Where logs are saved                            |
| `devices`      | Configurations of sensors, actuators, cameras |
| `relay_module` | Hardware relay pin mapping                      |
| `budgets`      | Device operation schedules/time limits         |
 

## Sensor Interfacing

All the sensors defined in STRUCTURE are I2C-based devices (excluding the USB-based cameras). To communicate with the I2C-based sensors, we utilize the `busio`, `board`, and sensor-specific packages (ex: for the TSL2591, utilizing the `adafruit_tca9548a` package). For the cameras, we utilize OpenCV2's library to connect and retrieve images.

Each sensor is defined in its own Python file under the `{ROOT}/devices/sensor/` folder and have a shared structure. Typically, a given sensor will have the following as a minimum skeleton:

```python

class SensorExample:
    def __init__(
        self,
        address: int,
        description: str,
        use_multi_channel = False,
        skip_on_fail = True
        # Sensor-specific parameters (ex: temperature unit for temperature sensor)
    ):
        # Define class members:
        self.address = address
        self.description = description # We use this description in main application for debugging and logging
        self.use_multi_channel = use_multi_channel # We utilize an i2c multiplexer hub that expands the number of i2c devices we can use; It changes the behavior of connection when defined
        self.skip_on_fail = skip_on_fail # Some connection behavior that helps for debugging 
        # etc...

        # Connect to sensor; we encapsulate connecton behavior into its own function because it can get complicated with retries, skipping on fail, and reporting back connection status:
        self.i2c_fail = False
        self.__connect__(self.sensor_obj, skip_on_fail=self.skip_on_fail)

    @property
    def readable(self):
        return not self.i2c_fail

    def __connect__(self, sensor_obj, skip_on_fail):
        # Define I2C object and attempt connection with your connection method:
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor_obj = create_sensor_obj(self.i2c) # You must define this based on how your sensor wants to be interfaced!
        except Exception as e:
            self.i2c_fail = True
            if not skip_on_fail:
                raise e

    def create_sensor_obj(self, i2c_conn):
        raise NotImplementedError

    def __call__(self):
        # The whole point of a given sensor is to read it!
        # Call your i2c object's read function (if applicable)
        data = self.sensor_obj.read() # Let's assume this read function generates two outputs (data_1, data_2)
        return {"data_1": data[0], "data_2": data[1]}
```

Obviously, for the camera code, the structure will not utilize the I2C-related libraries and would call the equivalent OpenCV2 calls. Additionally, USB-based cameras just have a USB ID for connection details. Based on what USB port you plug each camera into, the USB ID might be different than what's defined in this project. Please, use CLI commands like `lsusb` or connect to each camera to figure out what ID to use.

The following is an equivalent set of code for camera: 

``` python
import cv2
import numpy as np

# Assume the class structure has been defined already:
class Camera:
    def __init__(self, camera_id: int, ...):
        ...
        self.cap = self.__connect__(self, camera_id)

    def __connect__(self, camera_id:int):
        camera_obj = cv2.VideoCapture(camera_id)
        if not camera_obj.isOpened():
            raise ConnectionError("Failed to connect to USB Camera at ID {}".format(self.camera_id))
        return camera_obj

    def __call__(self) -> np.ndarray:
        # Return camera data by calling VideoCapture read function:
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Failed to grab camera frame!")
        
        # frame object is returned as a NumPy matrix with the following matrix dimension: (height, weight, 3)
        # The third channels in the last dimension represent an RGB value at H_n, and W_n position
        return frame
```  

The typical usage for these sensor classes is in two parts:

* Initialize the class object at program startup (ex: `sensor_obj = SensorExample()`)
* Call class object within the program (ex: `data = sensor_obj()`)

## Relay Interfacing

In contrast to the sensors' reliance on the relatively complicated I2C interface, the TSL0012 relay module is addressable via a set of GPIO pins. Each relay module acts independently from one another, and each actively used relay module is connected to its respective GPIO pin on the Raspberry PI. We can use the `gpiozero` Python package to read or write a pin to a true/false state. 

## Scheduling Tasks

**TODO**

## Main Loop

**TODO**

## API Reference

### Sensor

#### SHT