import os
import sys
import numpy as np
from typing import *
from enum import Enum
import cv2
import numpy as np
import time
from datetime import datetime

class GC0307_RESOLUTION(Enum):
    RES640P = (640, 480)


class GC0307:
    """A class for interfacing with the GC0307 camera module using OpenCV.

    This class provides an interface to capture frames, save images, and manage
    the camera stream. It allows users to configure resolution, capture images
    with timestamped filenames, and store them in a structured directory.

    Args:
        cam_id (int): The camera device index (e.g., `0`, `1`, `2`).
        camera_description (str): A descriptive name for the camera (used in folder naming).
        resolution_profile (GC0307_RESOLUTION): The desired camera resolution profile.
        save_path (str): The base directory where captured images will be stored.

    Example:
        >>> from devices.camera import GC0307, GC0307_RESOLUTION
        >>> cam = GC0307(0, "front_cam", GC0307_RESOLUTION.RES640P, "./images")
        >>> ret, frame = cam.read()
        >>> if ret:
        ...     print(frame.shape)
        ...     cam("test_%Y%m%d_%H%M%S")  # Captures and saves a timestamped image
        >>> cam.release()
    """

    def __init__(self, cam_id: int, camera_description: str, resolution_profile, save_path:str, fake_data=False):
        """Initializes the GC0307 camera interface.

        Args:
            cam_id (int): The ID of the camera device (as recognized by OpenCV).
            camera_description (str): A descriptive name for this camera (used in save path).
            resolution_profile (GC0307_RESOLUTION): The desired camera resolution.
            save_path (str): Directory where captured images will be saved.

        Raises:
            FileNotFoundError: If the specified save directory cannot be created.
            ValueError: If the camera fails to initialize properly.

        Example:
            >>> cam = GC0307(0, "lab_camera", GC0307_RESOLUTION.RES640P, "./captures")
        """
        self.__desc__ = camera_description
        self.res = resolution_profile.value
        self.__cap__ = cv2.VideoCapture(cam_id)
        self.__cap__.set(cv2.CAP_PROP_FRAME_WIDTH, self.res[0])
        self.__cap__.set(cv2.CAP_PROP_FRAME_HEIGHT, self.res[1])
        self.save_path = os.path.join(save_path, camera_description)
        self.fake_data = fake_data
        os.makedirs(self.save_path, exist_ok=True)

    def read(self) -> Tuple[bool, np.ndarray]:
        """Reads a single frame from the camera.

        Returns:
            Tuple[bool, np.ndarray]: A tuple where the first element indicates
            success (`True` or `False`), and the second is the captured frame
            as a NumPy array.

        Raises:
            RuntimeError: If the camera is not opened or accessible.

        Example:
            >>> ret, frame = cam.read()
            >>> if ret:
            ...     cv2.imshow("Frame", frame)
        """
        if self.fake_data:
            return (True, np.zeros((self.res[1], self.res[0]), dtype=np.uint8))
        return self.__cap__.read()

    def release(self):
        """Releases the camera resource.

        This method should always be called when done using the camera
        to free system resources.

        Example:
            >>> cam.release()
        """
        if not self.fake_data:
            self.__cap__.release()

    @property
    def readable(self):
        """Indicates whether the camera device is currently opened and readable.

        Returns:
            bool: `True` if the camera is open and operational, otherwise `False`.

        Example:
            >>> if cam.readable:
            ...     print("Camera is ready.")
        """
        if self.fake_data:
            return True
        return self.__cap__.isOpened()

    @property
    def description(self):
        """Returns the descriptive name of the camera.

        Returns:
            str: The description provided during initialization.

        Example:
            >>> cam.description
            'front_camera'
        """
        return self.__desc__

    def __call__(self, datetime_format="%Y-%m-%d_%H-%M-%S"):
        """Captures and saves a single image with a timestamped filename.

        The image is saved in the directory associated with the camera's description.

        Args:
            datetime_format (str, optional): Format string for timestamp filenames.
                Defaults to "%Y-%m-%d_%H-%M-%S".

        Returns:
            dict: A dictionary containing the path to the saved image.

        Raises:
            ValueError: If the camera fails to read a frame.

        Example:
            >>> result = cam("%Y%m%d_%H%M%S")
            >>> print(result["save_path"])
            './images/front_cam/2025-10-25_14-20-00.jpg'
        """
        timestamp = datetime.now()
        timestamp_str = "{}.jpg".format(timestamp.strftime(datetime_format))
        _image_path = os.path.join(self.save_path, timestamp_str)
        ret, img = self.read()
        if not ret:
            raise ValueError("Failed to read frame!")
        cv2.imwrite(_image_path, img)
        return {"name": timestamp_str, "save_path": _image_path}

if __name__ == "__main__":
    cam = GC0307(2, "main", GC0307_RESOLUTION.RES640P, "camera_1")
    ret, frame = cam.read()
    print(frame.shape)
    cv2.imwrite("test.png", frame)
    cam.release()
