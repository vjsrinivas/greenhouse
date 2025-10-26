<!-- markdownlint-disable -->

<a href="../../devices/instrument/light.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `light.py`






---

## <kbd>class</kbd> `LightBulb`
A class to control a light bulb connected to a relay module. 

This class provides simple methods to turn a light bulb on or off through a relay interface. It also supports toggling the light state dynamically. 



**Args:**
 
 - <b>`device_name`</b> (str):  The key or name of the light device in the relay module. 
 - <b>`relay_module`</b> (RelayModule):  The relay module or GPIO interface used to control the light. 



**Example:**
 ``` from devices.relay import RelayModule```
    >>> relay = RelayModule()
    >>> relay.add_device("light1", gpio_pin=17)
    >>> bulb = LightBulb("light1", relay)
    >>> bulb.trigger(True)   # Turns the light on
    {'state': True}
    >>> bulb.trigger()       # Toggles the light (off)
    {'state': False}


<a href="../../devices/instrument/light.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(device_name: str, relay_module: RelayModule)
```

Initializes a LightBulb instance. 



**Args:**
 
 - <b>`device_name`</b> (str):  The name or key of the light in the relay module. 
 - <b>`relay_module`</b> (RelayModule):  The relay module interface controlling the light. 



**Example:**
 ``` bulb = LightBulb("bedroom_light", relay)```



---

#### <kbd>property</kbd> keys

Returns the list of accessible property keys for the light. 



**Returns:**
 
 - <b>`list[str]`</b>:  A list containing `"state"` as the only key. 



**Example:**
 ``` bulb.keys```
    ['state']


---

#### <kbd>property</kbd> readable

Indicates whether the light state can be read externally. 



**Returns:**
 
 - <b>`bool`</b>:  Always returns `True`. 



**Example:**
 ``` bulb.readable```
    True


---

#### <kbd>property</kbd> state

Gets the current operational state of the light. 



**Returns:**
 
 - <b>`bool`</b>:  `True` if the light is on, otherwise `False`. 



**Example:**
 ``` bulb.state```
    False




---

<a href="../../devices/instrument/light.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `start_light`

```python
start_light()
```

Turns the light on by activating the corresponding relay. 



**Raises:**
 
 - <b>`KeyError`</b>:  If the device name is not found in the relay module. 
 - <b>`AttributeError`</b>:  If the relay device does not have an `.on()` method. 



**Example:**
 ``` bulb.start_light()```


---

<a href="../../devices/instrument/light.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `stop_light`

```python
stop_light()
```

Turns the light off by deactivating the corresponding relay. 



**Raises:**
 
 - <b>`KeyError`</b>:  If the device name is not found in the relay module. 
 - <b>`AttributeError`</b>:  If the relay device does not have an `.off()` method. 



**Example:**
 ``` bulb.stop_light()```


---

<a href="../../devices/instrument/light.py#L75"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `trigger`

```python
trigger(state: bool | None = None) → dict
```

Toggles or sets the light state. 

If `state` is not provided, the light toggles its current state. If `state` is explicitly given (`True` or `False`), the light is turned on or off accordingly. 



**Args:**
 
 - <b>`state`</b> (bool | None, optional):  Desired light state. If `None`, toggles the light state. Defaults to None. 



**Returns:**
 
 - <b>`dict`</b>:  A dictionary containing the current `"state"` of the light. 



**Raises:**
 
 - <b>`KeyError`</b>:  If the device name is not found in the relay module. 
 - <b>`AttributeError`</b>:  If the relay device lacks `on()` or `off()` methods. 



**Example:**
 ``` bulb.trigger(True)   # Turns the light on```
    {'state': True}
    >>> bulb.trigger(False)  # Turns the light off
    {'state': False}
    >>> bulb.trigger()       # Toggles the current state
    {'state': True}



