<!-- markdownlint-disable -->

<a href="../../devices/sensor/sht31d.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `sht31d.py`




**Global Variables**
---------------
- **TYPE_CHECKING**


---

## <kbd>class</kbd> `TemperatureSensor`
Interface for an SHT31D temperature and humidity sensor. 

This class manages the connection to an SHT31D sensor over I2C, allowing temperature (in Celsius or Fahrenheit) and relative humidity readings. It also supports usage with a TCA9548A multiplexer for multi-channel setups. 



**Args:**
 
 - <b>`address`</b> (int):  The I2C address of the sensor or multiplexer channel. 
 - <b>`description`</b> (str):  A user-defined description of the sensor. 
 - <b>`temp_unit`</b> (str, optional):  Unit in which temperature values are reported.  Must be either `"celsius"` or `"fahrenheit"`. Default is `"celsius"`. 
 - <b>`skip_on_fail`</b> (bool, optional):  If True, sensor connection failures will not  raise an exception. Default is True. 
 - <b>`use_multi_channel`</b> (bool, optional):  If True, attempts connection through a  TCA9548A multiplexer. Default is False. 



**Raises:**
 
 - <b>`ValueError`</b>:  If an unsupported temperature unit is provided. 
 - <b>`Exception`</b>:  If connection fails and `skip_on_fail` is False. 



**Example:**
 ``` sensor = TemperatureSensor(address=0x44, description="Greenhouse sensor")```
    >>> sensor.readable
    True
    >>> sensor.temperature
    22.5
    >>> sensor.relative_humidity
    45.3


<a href="../../devices/sensor/sht31d.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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






---

#### <kbd>property</kbd> keys

Data keys provided by the sensor. 



**Returns:**
 
 - <b>`list of str`</b>:  Always `["temperature", "relative_humidity"]`. 



**Example:**
 ``` sensor = TemperatureSensor(0x44, "Test sensor")```
    >>> sensor.keys
    ['temperature', 'relative_humidity']


---

#### <kbd>property</kbd> readable

Whether the sensor is successfully readable. 



**Returns:**
 
 - <b>`bool`</b>:  True if sensor is working, False if initialization failed. 



**Example:**
 ``` sensor = TemperatureSensor(0x44, "Test sensor")```
    >>> sensor.readable
    True


---

#### <kbd>property</kbd> relative_humidity

Whether the sensor is successfully readable. 



**Returns:**
 
 - <b>`bool`</b>:  True if sensor is working, False if initialization failed. 



**Example:**
 ``` sensor = TemperatureSensor(0x44, "Test sensor")```
    >>> sensor.readable
    True


---

#### <kbd>property</kbd> temperature

Current temperature reading from the sensor. 



**Returns:**
 
 - <b>`float`</b>:  Temperature value in Celsius or Fahrenheit depending on `temp_unit`. 



**Raises:**
 
 - <b>`ValueError`</b>:  If an unsupported unit is set for `temp_unit`. 



**Example:**
 ``` sensor = TemperatureSensor(0x44, "Test sensor")```
    >>> sensor.temperature
    21.7







---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
