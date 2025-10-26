from devices.relay import RelayModule
from threading import Thread
import time
from loguru import logger


class WaterPump:
    """A class to control a water pump connected to a relay module.

    This class currently supports **timer-based automatic operation**.
    The water pump runs in a background thread for a defined duration and spacing interval.
    Future versions may include integration with a soil moisture sensor for smarter irrigation.

    Args:
        device_name (str): The key or name of the pump device in the relay module.
        relay_module (RelayModule): The relay module interface controlling the pump.
        period_spacing_sec (int | float, optional): Time interval (in seconds) between watering cycles. Defaults to 10.
        period (int | float, optional): Total duration (in seconds) for the watering period. Defaults to 5.

    Example:
        >>> from devices.relay import RelayModule
        >>> relay = RelayModule()
        >>> relay.add_device("pump1", gpio_pin=21)
        >>> pump = WaterPump("pump1", relay, period_spacing_sec=15, period=10)
        >>> pump.trigger(True)  # Starts the watering cycle in a background thread
    """

    def __init__(self, device_name: str, relay_module: RelayModule, period_spacing_sec: int = 10, period: int = 5):
        """Initializes the WaterPump instance.

        NOTE: This class is timer-based only. Future addition
        might utilized a soil sensor to report back moisture content.
        Moisture content can be used to trigger "smarter" watering
        behavior

        Args:
            device_name (str): The key or name of the pump device in the relay module.
            relay_module (RelayModule): The relay module interface controlling the pump.
            period_spacing_sec (int | float, optional): The spacing time between watering cycles. Defaults to 10.
            period (int | float, optional): The total watering period in seconds. Defaults to 5.

        Example:
            >>> pump = WaterPump("garden_pump", relay, period_spacing_sec=30, period=10)
        """
        self.__relay__ = relay_module
        self.__dev__ = device_name
        self.__state__ = False
        self.period_spacing_sec = period_spacing_sec  # seconds between cycles
        self.period = period # seconds

        self.thread_duration = 0.0
        self.thread_start = False
        self.active_thread = None

    def start_pump(self):
        """Activates the water pump by switching on the relay.

        Raises:
            KeyError: If the device name is not found in the relay module.
            AttributeError: If the relay device does not implement `.on()`.

        Example:
            >>> pump.start_pump()
        """
        self.__relay__[self.__dev__].on()

    def stop_pump(self):
        """Deactivates the water pump by switching off the relay.

        Raises:
            KeyError: If the device name is not found in the relay module.
            AttributeError: If the relay device does not implement `.off()`.

        Example:
            >>> pump.stop_pump()
        """
        self.__relay__[self.__dev__].off()

    def __thread_function__(self, period_spacing_sec: int | float = 10, period_sec: int | float = 5):
        """Internal function to run the pump in a timed cycle using a background thread.

        This function controls the timing and duration of the pump operation.
        It can be extended in future implementations to respond dynamically
        to sensor data (e.g., soil moisture).

        Args:
            period_spacing_sec (int | float, optional): The spacing between watering cycles in seconds.
            period_sec (int | float, optional): The total duration of the watering period in seconds.

        Returns:
            None

        Example:
            >>> pump._WaterPump__thread_function__(period_spacing_sec=10, period_sec=5)
        """
        t1 = time.time()
        # NOTE: Enable once water bucket is filled with water
        # self.start_pump()

        while True:
            if period_spacing_sec != -1:
                # NOTE: Enable once water bucket is filled with water
                # self.stop_pump()

                time.sleep(period_spacing_sec)
                # NOTE: Enable once water bucket is filled with water
                # self.start_pump()
            t2 = time.time()
            if t2-t1 > period_sec:
                break

        # NOTE: Enable once water bucket is filled with water
        # self.stop_pump()
        stop_duration = time.time() - t1
        self.thread_active = False
        self.iteration_on = False
        self.thread_duration = stop_duration
        logger.info("Water pump thread exiting after {} seconds".format(self.thread_duration))

    def trigger(self, state: bool):
        """Triggers the water pump operation.

        This method starts the water pump’s timed cycle in a background thread.
        If a thread is already active, a warning message is logged instead.

        Args:
            state (bool): Desired state of the pump. Currently unused but reserved for future expansion.

        Returns:
            None

        Raises:
            Warning: Logs a warning if a pump thread is already active.

        Example:
            >>> pump.trigger(True)   # Starts the watering cycle
            >>> pump.trigger(False)  # (No effect currently)
        """
        self.__state__ = state # NOTE: Pointless
        if not self.thread_start:
            # Start pump thread; otherwise, skip with warning
            self.active_thread = Thread(target=self.__thread_function__, args=(self.period_spacing_sec, self.period))
            self.active_thread.start()
            self.thread_active = True
        else:
            logger.warning("Water pump thread is still active")

    @property
    def keys(self) -> list[str]:
        """Returns a list of readable property keys.

        Returns:
            list[str]: A list containing `"pump_time"` and `"duration"`.

        Example:
            >>> pump.keys
            ['pump_time', 'duration']
        """
        return ["pump_time", "duration"]

    @property
    def state(self) -> bool:
        """Gets the current operational state of the water pump.

        Returns:
            bool: `True` if the pump is active, otherwise `False`.

        Example:
            >>> pump.state
            False
        """
        return self.__state__

    @property
    def readable(self) -> bool:
        """Indicates whether the water pump's state can be read externally.

        Returns:
            bool: Always returns `True`.

        Example:
            >>> pump.readable
            True
        """
        return True
