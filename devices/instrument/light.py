from devices.relay import RelayModule

class LightBulb:
    """A class to control a light bulb connected to a relay module.

    This class provides simple methods to turn a light bulb on or off through
    a relay interface. It also supports toggling the light state dynamically.

    Args:
        device_name (str): The key or name of the light device in the relay module.
        relay_module (RelayModule): The relay module or GPIO interface used to control the light.

    Example:
        >>> from devices.relay import RelayModule
        >>> relay = RelayModule()
        >>> relay.add_device("light1", gpio_pin=17)
        >>> bulb = LightBulb("light1", relay)
        >>> bulb.trigger(True)   # Turns the light on
        {'state': True}
        >>> bulb.trigger()       # Toggles the light (off)
        {'state': False}
    """

    def __init__(self, device_name: str, relay_module: RelayModule):
        """Initializes a LightBulb instance.

        Args:
            device_name (str): The name or key of the light in the relay module.
            relay_module (RelayModule): The relay module interface controlling the light.

        Example:
            >>> bulb = LightBulb("bedroom_light", relay)
        """
        self.__relay__ = relay_module
        self.__dev__ = device_name
        self.__state__ = False  # False -> off; True -> on

    def start_light(self):
        """Turns the light on by activating the corresponding relay.

        Raises:
            KeyError: If the device name is not found in the relay module.
            AttributeError: If the relay device does not have an `.on()` method.

        Example:
            >>> bulb.start_light()
        """
        self.__relay__[self.__dev__].on()

    def stop_light(self):
        """Turns the light off by deactivating the corresponding relay.

        Raises:
            KeyError: If the device name is not found in the relay module.
            AttributeError: If the relay device does not have an `.off()` method.

        Example:
            >>> bulb.stop_light()
        """
        self.__relay__[self.__dev__].off()

    @property
    def keys(self) -> list[str]:
        """Returns the list of accessible property keys for the light.

        Returns:
            list[str]: A list containing `"state"` as the only key.

        Example:
            >>> bulb.keys
            ['state']
        """
        return ["state"]

    def trigger(self, state: bool | None = None) -> dict:
        """Toggles or sets the light state.

        If `state` is not provided, the light toggles its current state.
        If `state` is explicitly given (`True` or `False`), the light is turned
        on or off accordingly.

        Args:
            state (bool | None, optional): Desired light state. If `None`, toggles the light state. Defaults to None.

        Returns:
            dict: A dictionary containing the current `"state"` of the light.

        Raises:
            KeyError: If the device name is not found in the relay module.
            AttributeError: If the relay device lacks `on()` or `off()` methods.

        Example:
            >>> bulb.trigger(True)   # Turns the light on
            {'state': True}
            >>> bulb.trigger(False)  # Turns the light off
            {'state': False}
            >>> bulb.trigger()       # Toggles the current state
            {'state': True}
        """
        # Toggle states if state is not defined!
        if state is None:
            state = not self.__state__

        if state:
            self.start_light()
        else:
            self.stop_light()
        self.__state__ = state
        return {"state": state}

    @property
    def state(self) -> bool:
        """Gets the current operational state of the light.

        Returns:
            bool: `True` if the light is on, otherwise `False`.

        Example:
            >>> bulb.state
            False
        """
        return self.__state__

    @property
    def readable(self) -> bool:
        """Indicates whether the light state can be read externally.

        Returns:
            bool: Always returns `True`.

        Example:
            >>> bulb.readable
            True
        """
        return True
