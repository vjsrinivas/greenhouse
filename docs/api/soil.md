<!-- markdownlint-disable -->

<a href="../../devices/sensor/soil.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `soil.py`




**Global Variables**
---------------
- **TYPE_CHECKING**


---

## <kbd>class</kbd> `SoilSensor`
A class for interfacing with Adafruit STEMMA-compatible soil sensors (Seesaw). 

This class provides access to soil moisture and temperature readings over I²C. It supports both single-channel and multi-channel configurations (via TCA9548A multiplexer). 



**Args:**
 
 - <b>`address`</b> (int):  I²C address or channel index of the soil sensor. 
 - <b>`description`</b> (str):  A descriptive name for the sensor instance. 
 - <b>`temp_unit`</b> (Literal["celsius", "fahrenheit"], optional):  Unit for temperature readings. Defaults to `"celsius"`. 
 - <b>`skip_on_fail`</b> (bool, optional):  Whether to skip sensor initialization errors instead of raising exceptions. Defaults to `True`. 
 - <b>`use_multi_channel`</b> (bool, optional):  Whether to connect through a TCA9548A multiplexer. Defaults to `False`. 



**Raises:**
 
 - <b>`ValueError`</b>:  If an invalid temperature unit is provided. 
 - <b>`RuntimeError`</b>:  If sensor initialization fails and `skip_on_fail` is `False`. 



**Example:**
 ``` from devices.soil_sensor import SoilSensor```
    >>> sensor = SoilSensor(0x36, "garden_sensor_1")
    >>> print(sensor.moisture)
    542
    >>> print(sensor.temperature)
    23.4


<a href="../../devices/sensor/soil.py#L36"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    address: int,
    description: str,
    temp_unit: Literal['celsius', 'fahrenheit'] = 'celsius',
    skip_on_fail=True,
    use_multi_channel=False
)
```

Initializes the soil sensor and establishes an I²C connection. 



**Args:**
 
 - <b>`address`</b> (int):  I²C address (e.g., `0x36`) or multiplexer channel number. 
 - <b>`description`</b> (str):  A descriptive name for the sensor. 
 - <b>`temp_unit`</b> (Literal["celsius", "fahrenheit"], optional):  Desired temperature unit. Defaults to `"celsius"`. 
 - <b>`skip_on_fail`</b> (bool, optional):  Whether to suppress initialization errors. Defaults to `True`. 
 - <b>`use_multi_channel`</b> (bool, optional):  Whether to use a TCA9548A multiplexer. Defaults to `False`. 



**Raises:**
 
 - <b>`ValueError`</b>:  If `temp_unit` is not `"celsius"` or `"fahrenheit"`. 
 - <b>`RuntimeError`</b>:  If initialization fails and `skip_on_fail` is `False`. 



**Example:**
 ``` sensor = SoilSensor(2, "multi_channel_sensor", use_multi_channel=True)```



---

#### <kbd>property</kbd> moisture

Reads the current soil moisture level. 



**Returns:**
 
 - <b>`int`</b>:  The moisture level as a raw sensor value (0–1023 range for most devices). 



**Raises:**
 
 - <b>`RuntimeError`</b>:  If the sensor is not connected or readable. 



**Example:**
 ``` print(sensor.moisture)```
    512


---

#### <kbd>property</kbd> readable

Checks if the soil sensor is readable (I²C connection is healthy). 



**Returns:**
 
 - <b>`bool`</b>:  `True` if sensor is readable, otherwise `False`. 



**Example:**
 ``` if sensor.readable:```
    ...     print("Sensor connected and active.")


---

#### <kbd>property</kbd> temperature

Reads the current temperature from the soil sensor. 



**Returns:**
 
 - <b>`float`</b>:  Temperature in Celsius or Fahrenheit depending on configuration. 



**Raises:**
 
 - <b>`RuntimeError`</b>:  If the sensor is not connected or readable. 
 - <b>`ValueError`</b>:  If an unknown temperature unit is encountered. 



**Example:**
 ``` print(sensor.temperature)```
    24.3





