<!-- markdownlint-disable -->

<a href="../../devices/sensor/camera.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `camera.py`




**Global Variables**
---------------
- **TYPE_CHECKING**


---

## <kbd>class</kbd> `GC0307`
A class for interfacing with the GC0307 camera module using OpenCV. 

This class provides an interface to capture frames, save images, and manage the camera stream. It allows users to configure resolution, capture images with timestamped filenames, and store them in a structured directory. 



**Args:**
 
 - <b>`cam_id`</b> (int):  The camera device index (e.g., `0`, `1`, `2`). 
 - <b>`camera_description`</b> (str):  A descriptive name for the camera (used in folder naming). 
 - <b>`resolution_profile`</b> (GC0307_RESOLUTION):  The desired camera resolution profile. 
 - <b>`save_path`</b> (str):  The base directory where captured images will be stored. 



**Example:**
 ``` from devices.camera import GC0307, GC0307_RESOLUTION```
    >>> cam = GC0307(0, "front_cam", GC0307_RESOLUTION.RES640P, "./images")
    >>> ret, frame = cam.read()
    >>> if ret:
    ...     print(frame.shape)
    ...     cam("test_%Y%m%d_%H%M%S")  # Captures and saves a timestamped image
    >>> cam.release()


<a href="../../devices/sensor/camera.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    cam_id: int,
    camera_description: str,
    resolution_profile,
    save_path: str
)
```

Initializes the GC0307 camera interface. 



**Args:**
 
 - <b>`cam_id`</b> (int):  The ID of the camera device (as recognized by OpenCV). 
 - <b>`camera_description`</b> (str):  A descriptive name for this camera (used in save path). 
 - <b>`resolution_profile`</b> (GC0307_RESOLUTION):  The desired camera resolution. 
 - <b>`save_path`</b> (str):  Directory where captured images will be saved. 



**Raises:**
 
 - <b>`FileNotFoundError`</b>:  If the specified save directory cannot be created. 
 - <b>`ValueError`</b>:  If the camera fails to initialize properly. 



**Example:**
 ``` cam = GC0307(0, "lab_camera", GC0307_RESOLUTION.RES640P, "./captures")```



---

#### <kbd>property</kbd> description

Returns the descriptive name of the camera. 



**Returns:**
 
 - <b>`str`</b>:  The description provided during initialization. 



**Example:**
 ``` cam.description```
    'front_camera'


---

#### <kbd>property</kbd> readable

Indicates whether the camera device is currently opened and readable. 



**Returns:**
 
 - <b>`bool`</b>:  `True` if the camera is open and operational, otherwise `False`. 



**Example:**
 ``` if cam.readable:```
    ...     print("Camera is ready.")




---

<a href="../../devices/sensor/camera.py#L62"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `read`

```python
read() → Tuple[bool, ndarray]
```

Reads a single frame from the camera. 



**Returns:**
 
 - <b>`Tuple[bool, np.ndarray]`</b>:  A tuple where the first element indicates success (`True` or `False`), and the second is the captured frame as a NumPy array. 



**Raises:**
 
 - <b>`RuntimeError`</b>:  If the camera is not opened or accessible. 



**Example:**
 ``` ret, frame = cam.read()```
    >>> if ret:
    ...     cv2.imshow("Frame", frame)


---

<a href="../../devices/sensor/camera.py#L80"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `release`

```python
release()
```

Releases the camera resource. 

This method should always be called when done using the camera to free system resources. 



**Example:**
 ``` cam.release()```



---

## <kbd>class</kbd> `GC0307_RESOLUTION`








