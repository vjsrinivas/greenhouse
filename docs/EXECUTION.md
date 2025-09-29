# Starting the Greenhouse

## Software

Before running the Python application, please install the required Python packages to the active Python installation. **It is highly advised that you utilize some kind of virtual Python environment to avoid any package conflicts.** For simplicity sake, you can utilize the in-built `venv` tool:

``` bash
# Create a new Python virtual environment in {ROOT}:
cd ${ROOT}
python3 -m venv greenhouse # This will name the virtual environment as "greenhouse". If you're going to use the provided service file and bash scripts, this name is required!

# Activte the environment:
source greenhouse/scripts/activate
# After activating the environment, you should see the next bash line with that environment: $ (greenhouse) ~/${ROOT}

# Navigate into the greenhouse repo and install required packages:
cd ${ROOT}/greenhouse
pip install -r requirements.txt
```

Please note that package version eglibility is based on the Python version. This project assumes Python 3.11.

The main greenhouse application defined in [PROGRAMMING](./docs/PROGRAMMING.md) section should start automatically when powered. You can define this in the Raspberry Pi by creating a systemd configuration that triggers the `greenhouse` environment, the traversal to the `greenhouse` directory, and the execution of the `python3 main.py` command:

``` bash
# NOTE: Please ensure your current user has the proper privileges to add systemd services
# Define your service file path here:
SERVICE_FILE_PATH="/path/to/file"

sudo systemctl daemon-reload
sudo cp $SERVICE_FILE_PATH /etc/systemd/system/
sudo systemctl enable greenhouse.service
sudo systemctl start greenhouse.service
sudo systemctl daemon-reload
```

To make this part automated, this project has provided a sample service file (`greenhouse.service`) as well as a `setup.sh` and `disable.sh` to add the greenhouse service file to the RPI5 and to stop & remove the service, respectively.

## Hardware
Always double-check that all your wiring is secure and organized (hopefully better than this guide). To start the hardware, simply plug in the surge protector to a wall outlet. Verify that the 5V DC power adapter, the relay, and the RPi5 all have their LED indicator statuses on. Additionally, ensure that the RPi5 has an established green light. If the LED briefly starts as green and turns and stays red, this could be an indication of an improper connection between the 5v and ground rails to the DC PDB. 

# Monitoring Systems

## Software
### Monitoring Logs
When creating the systemd configuration, the logs will be recorded in `[INSERT SYSTEMD COMMAND FOR LOGS]`. The logs are also recorded locally in the `/${GREENHOUSE}/logs` via loguru. The loguru configuration is setup in a way that logs expire after a X-amount of time.

## Monitoring Device Statuses
On startup, the application checks if every sensor defined in the configuration file can be detected and read from. The same cannot be said about the GPIO connections to the relay. It will be up to you to ensure that all devices connected to the relay are triggerable. The recommended way is to use `relay.py` in the devices folder:

```bash
python relay.py --pin 23 --on # or whatever the pin you've assigned that specific relay to
```

## Hardware
### 