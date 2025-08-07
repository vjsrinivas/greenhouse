import os
import sys
import numpy as np
from typing import *
from enum import Enum
import cv2
import numpy as np


class GC0307_RESOLUTION(Enum):
    RES640P = (640, 480)


class GC0307:
    def __init__(self, cam_id: int, camera_description: str, resolution_profile):
        self.__desc__ = camera_description
        self.res = resolution_profile.value
        self.__cap__ = cv2.VideoCapture(cam_id)
        self.__cap__.set(cv2.CAP_PROP_FRAME_WIDTH, self.res[0])
        self.__cap__.set(cv2.CAP_PROP_FRAME_HEIGHT, self.res[1])

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


if __name__ == "__main__":
    cam = GC0307(2, "main", GC0307_RESOLUTION.RES640P)
    ret, frame = cam.read()
    print(frame.shape)
    cv2.imwrite("test.png", frame)
    cam.release()
