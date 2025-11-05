import os
import sys
from threading import Thread
from loguru import logger
import time

class Fan:
    """A class to control a fan device through a relay module.

    This class provides functionality to control a fan via a relay interface.
    It supports both manual control (on/off) and timed operation in a background thread.

    Attributes:
        __relay__ (dict): A relay module interface for controlling devices.
        __dev__ (str): The name of the device assigned in the relay module.
        __state__ (bool): The current operational state of the fan (True for ON, False for OFF).
        __duration__ (int | float): The default duration in seconds for which the fan runs in timed mode.
        thread_start (bool): Indicates whether a background fan control thread is currently running.
        active_thread (Thread | None): The active thread instance managing fan operation, if any.

    Example:
        >>> from my_module import Fan
        >>> relay = {"fan1": SomeRelayObject()}
        >>> fan = Fan("fan1", relay, duration=5)
        >>> fan.trigger()  # Runs the fan for 5 seconds
        {'state': True}
        >>> fan.trigger(False)  # Turns the fan off manually
        {'state': False}
    """

    def __init__(self, device_name: str, relay_module, duration=10, fake_data=False):
        """Initializes a new Fan instance.

        Args:
            device_name (str): The key or name of the fan device in the relay module.
            relay_module (dict): A relay module or GPIO controller interface.
            duration (int | float, optional): The duration (in seconds) for which the fan runs in timed mode. Defaults to 10.

        Example:
            >>> relay = {"fan": SomeRelayObject()}
            >>> fan = Fan("fan", relay, duration=8)
        """

        self.__relay__ = relay_module
        self.__dev__ = device_name
        self.__state__ = False # False -> off; True -> on
        self.__duration__ = duration
        self.thread_start = False
        self.active_thread = None
        self.fake_data = fake_data

    def start_fan(self):
        """Turns the fan on by activating the corresponding relay.

        Raises:
            KeyError: If the device name is not found in the relay module.

        Example:
            >>> fan.start_fan()  # Activates the fan
        """
        if not self.fake_data:
            self.__relay__[self.__dev__].on()

    def stop_fan(self):
        """Turns the fan off by deactivating the corresponding relay.

        Raises:
            KeyError: If the device name is not found in the relay module.

        Example:
            >>> fan.stop_fan()  # Deactivates the fan
        """
        if not self.fake_data:
            self.__relay__[self.__dev__].off()

    def __thread_function__(self, duration):
        """Internal function to run the fan for a specified duration in a separate thread.

        Args:
            duration (int | float): The duration (in seconds) the fan should stay on.

        Returns:
            float: The actual duration (in seconds) that the fan remained active.

        Example:
            >>> fan._Fan__thread_function__(5)
            5.00123
        """
        start_time = time.time()
        active_duration = time.time() - start_time
        
        self.start_fan()
        while active_duration < self.__duration__:
            active_duration = time.time() - start_time
        self.stop_fan()
        self.thread_start=False
        return active_duration

    @property
    def keys(self):
        """Returns a list of accessible state keys for the fan.

        Returns:
            list[str]: A list containing `"state"` as the only key.

        Example:
            >>> fan.keys
            ['state']
        """
        return ["state"]

    def trigger(self, state:bool=None):
        """Triggers the fan to run manually or automatically.

        If `state` is `None`, the fan runs for a preset duration in a background thread.
        If `state` is `True` or `False`, it immediately turns the fan on or off, respectively.

        Args:
            state (bool | None, optional): Desired fan state. If `None`, activates timed mode. Defaults to None.

        Returns:
            dict: A dictionary indicating the fan's current `"state"`.

        Raises:
            Warning: Logs a warning (via `loguru`) if a control thread is already active.
            KeyError: If the device name is invalid in the relay module.

        Example:
            >>> fan.trigger()        # Starts the fan in timed mode
            {'state': True}
            >>> fan.trigger(True)    # Turns on the fan manually
            {'state': True}
            >>> fan.trigger(False)   # Turns off the fan manually
            {'state': False}
        """
        
        if state is None:
            # Start thread function!
            if not self.thread_start:
                # start pump thread; otherwise, skip with warning
                self.active_thread = Thread(target=self.__thread_function__, args=(self.__duration__,))
                self.active_thread.start()
                self.thread_start = True
            else:
                logger.warning("Fan thread is still active")
            
            return {"state": True}
        else:
            if not self.thread_start:
                if state:
                    self.start_fan()
                else:
                    self.stop_fan()
                self.__state__ = state
            else:
                logger.warning("Fan thread is still active")

            return {"state": state}

    @property
    def state(self) -> bool:
        """Returns the current operational state of the fan.

        Returns:
            bool: `True` if the fan is on, otherwise `False`.

        Example:
            >>> fan.state
            False
        """
        return self.__state__

    @property
    def readable(self) -> bool:
        """Indicates whether the fan's state can be read.

        Returns:
            bool: Always returns `True`.

        Example:
            >>> fan.readable
            True
        """
        return True