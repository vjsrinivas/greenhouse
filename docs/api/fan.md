<!-- markdownlint-disable -->

<a href="../../devices/instrument/fan.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `fan.py`






---

## <kbd>class</kbd> `Fan`
A class to control a fan device through a relay module. 

This class provides functionality to control a fan via a relay interface. It supports both manual control (on/off) and timed operation in a background thread. 



**Attributes:**
 
 - <b>`__relay__`</b> (dict):  A relay module interface for controlling devices. 
 - <b>`__dev__`</b> (str):  The name of the device assigned in the relay module. 
 - <b>`__state__`</b> (bool):  The current operational state of the fan (True for ON, False for OFF). 
 - <b>`__duration__`</b> (int | float):  The default duration in seconds for which the fan runs in timed mode. 
 - <b>`thread_start`</b> (bool):  Indicates whether a background fan control thread is currently running. 
 - <b>`active_thread`</b> (Thread | None):  The active thread instance managing fan operation, if any. 



**Example:**
 ``` from my_module import Fan```
    >>> relay = {"fan1": SomeRelayObject()}
    >>> fan = Fan("fan1", relay, duration=5)
    >>> fan.trigger()  # Runs the fan for 5 seconds
    {'state': True}
    >>> fan.trigger(False)  # Turns the fan off manually
    {'state': False}


<a href="../../devices/instrument/fan.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(device_name: str, relay_module, duration=10)
```

Initializes a new Fan instance. 



**Args:**
 
 - <b>`device_name`</b> (str):  The key or name of the fan device in the relay module. 
 - <b>`relay_module`</b> (dict):  A relay module or GPIO controller interface. 
 - <b>`duration`</b> (int | float, optional):  The duration (in seconds) for which the fan runs in timed mode. Defaults to 10. 



**Example:**
 ``` relay = {"fan": SomeRelayObject()}```
    >>> fan = Fan("fan", relay, duration=8)



---

#### <kbd>property</kbd> keys

Returns a list of accessible state keys for the fan. 



**Returns:**
 
 - <b>`list[str]`</b>:  A list containing `"state"` as the only key. 



**Example:**
 ``` fan.keys```
    ['state']


---

#### <kbd>property</kbd> readable

Indicates whether the fan's state can be read. 



**Returns:**
 
 - <b>`bool`</b>:  Always returns `True`. 



**Example:**
 ``` fan.readable```
    True


---

#### <kbd>property</kbd> state

Returns the current operational state of the fan. 



**Returns:**
 
 - <b>`bool`</b>:  `True` if the fan is on, otherwise `False`. 



**Example:**
 ``` fan.state```
    False




---

<a href="../../devices/instrument/fan.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `start_fan`

```python
start_fan()
```

Turns the fan on by activating the corresponding relay. 



**Raises:**
 
 - <b>`KeyError`</b>:  If the device name is not found in the relay module. 



**Example:**
 ``` fan.start_fan()  # Activates the fan```


---

<a href="../../devices/instrument/fan.py#L62"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `stop_fan`

```python
stop_fan()
```

Turns the fan off by deactivating the corresponding relay. 



**Raises:**
 
 - <b>`KeyError`</b>:  If the device name is not found in the relay module. 



**Example:**
 ``` fan.stop_fan()  # Deactivates the fan```


---

<a href="../../devices/instrument/fan.py#L109"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `trigger`

```python
trigger(state: bool = None)
```

Triggers the fan to run manually or automatically. 

If `state` is `None`, the fan runs for a preset duration in a background thread. If `state` is `True` or `False`, it immediately turns the fan on or off, respectively. 



**Args:**
 
 - <b>`state`</b> (bool | None, optional):  Desired fan state. If `None`, activates timed mode. Defaults to None. 



**Returns:**
 
 - <b>`dict`</b>:  A dictionary indicating the fan's current `"state"`. 



**Raises:**
 
 - <b>`Warning`</b>:  Logs a warning (via `loguru`) if a control thread is already active. 
 - <b>`KeyError`</b>:  If the device name is invalid in the relay module. 



**Example:**
 ``` fan.trigger()        # Starts the fan in timed mode```
    {'state': True}
    >>> fan.trigger(True)    # Turns on the fan manually
    {'state': True}
    >>> fan.trigger(False)   # Turns off the fan manually
    {'state': False}



