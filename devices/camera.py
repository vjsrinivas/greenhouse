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
    def __init__(self, cam_id: int, camera_description: str, resolution_profile, save_path:str):
        self.__desc__ = camera_description
        self.res = resolution_profile.value
        self.__cap__ = cv2.VideoCapture(cam_id)
        self.__cap__.set(cv2.CAP_PROP_FRAME_WIDTH, self.res[0])
        self.__cap__.set(cv2.CAP_PROP_FRAME_HEIGHT, self.res[1])
        self.save_path = os.path.join(save_path, camera_description)
        os.makedirs(self.save_path, exist_ok=True)

    def read(self) -> Tuple[bool, np.ndarray]:
        return self.__cap__.read()

    def release(self):
        self.__cap__.release()

    @property
    def readable(self):
        return self.__cap__.isOpened()

    @property
    def description(self):
        return self.__desc__

    def __call__(self, datetime_format="%Y-%m-%d_%H-%M-%S"):
        timestamp = datetime.now()
        timestamp_str = "{}.jpg".format(timestamp.strftime(datetime_format))
        _image_path = os.path.join(self.save_path, timestamp_str)
        ret, img = self.read()
        if not ret:
            raise ValueError("Failed to read frame!")
        cv2.imwrite(_image_path, img)
        return {"save_path": _image_path}

if __name__ == "__main__":
    cam = GC0307(2, "main", GC0307_RESOLUTION.RES640P)
    ret, frame = cam.read()
    print(frame.shape)
    cv2.imwrite("test.png", frame)
    cam.release()
