<!-- markdownlint-disable -->

<a href="../../devices/instrument/water.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `water.py`






---

## <kbd>class</kbd> `WaterPump`
A class to control a water pump connected to a relay module. 

This class currently supports **timer-based automatic operation**. The water pump runs in a background thread for a defined duration and spacing interval. Future versions may include integration with a soil moisture sensor for smarter irrigation. 



**Args:**
 
 - <b>`device_name`</b> (str):  The key or name of the pump device in the relay module. 
 - <b>`relay_module`</b> (RelayModule):  The relay module interface controlling the pump. 
 - <b>`period_spacing_sec`</b> (int | float, optional):  Time interval (in seconds) between watering cycles. Defaults to 10. 
 - <b>`period`</b> (int | float, optional):  Total duration (in seconds) for the watering period. Defaults to 5. 



**Example:**
 ``` from devices.relay import RelayModule```
    >>> relay = RelayModule()
    >>> relay.add_device("pump1", gpio_pin=21)
    >>> pump = WaterPump("pump1", relay, period_spacing_sec=15, period=10)
    >>> pump.trigger(True)  # Starts the watering cycle in a background thread


<a href="../../devices/instrument/water.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    device_name: str,
    relay_module: RelayModule,
    period_spacing_sec: int = 10,
    period: int = 5
)
```

Initializes the WaterPump instance. 

NOTE: This class is timer-based only. Future addition might utilized a soil sensor to report back moisture content. Moisture content can be used to trigger "smarter" watering behavior 



**Args:**
 
 - <b>`device_name`</b> (str):  The key or name of the pump device in the relay module. 
 - <b>`relay_module`</b> (RelayModule):  The relay module interface controlling the pump. 
 - <b>`period_spacing_sec`</b> (int | float, optional):  The spacing time between watering cycles. Defaults to 10. 
 - <b>`period`</b> (int | float, optional):  The total watering period in seconds. Defaults to 5. 



**Example:**
 ``` pump = WaterPump("garden_pump", relay, period_spacing_sec=30, period=10)```



---

#### <kbd>property</kbd> keys

Returns a list of readable property keys. 



**Returns:**
 
 - <b>`list[str]`</b>:  A list containing `"pump_time"` and `"duration"`. 



**Example:**
 ``` pump.keys```
    ['pump_time', 'duration']


---

#### <kbd>property</kbd> readable

Indicates whether the water pump's state can be read externally. 



**Returns:**
 
 - <b>`bool`</b>:  Always returns `True`. 



**Example:**
 ``` pump.readable```
    True


---

#### <kbd>property</kbd> state

Gets the current operational state of the water pump. 



**Returns:**
 
 - <b>`bool`</b>:  `True` if the pump is active, otherwise `False`. 



**Example:**
 ``` pump.state```
    False




---

<a href="../../devices/instrument/water.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `start_pump`

```python
start_pump()
```

Activates the water pump by switching on the relay. 



**Raises:**
 
 - <b>`KeyError`</b>:  If the device name is not found in the relay module. 
 - <b>`AttributeError`</b>:  If the relay device does not implement `.on()`. 



**Example:**
 ``` pump.start_pump()```


---

<a href="../../devices/instrument/water.py#L67"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `stop_pump`

```python
stop_pump()
```

Deactivates the water pump by switching off the relay. 



**Raises:**
 
 - <b>`KeyError`</b>:  If the device name is not found in the relay module. 
 - <b>`AttributeError`</b>:  If the relay device does not implement `.off()`. 



**Example:**
 ``` pump.stop_pump()```


---

<a href="../../devices/instrument/water.py#L120"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `trigger`

```python
trigger(state: bool)
```

Triggers the water pump operation. 

This method starts the water pump’s timed cycle in a background thread. If a thread is already active, a warning message is logged instead. 



**Args:**
 
 - <b>`state`</b> (bool):  Desired state of the pump. Currently unused but reserved for future expansion. 



**Returns:**
 None 



**Raises:**
 
 - <b>`Warning`</b>:  Logs a warning if a pump thread is already active. 



**Example:**
 ``` pump.trigger(True)   # Starts the watering cycle```
    >>> pump.trigger(False)  # (No effect currently)



