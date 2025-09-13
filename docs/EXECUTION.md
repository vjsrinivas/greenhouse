# Starting the Greenhouse

## Software
The main greenhouse application defined in [PROGRAMMING](./docs/PROGRAMMING.md) section should start automatically. You can define this in the Raspberry Pi by creating a systemd configuration that triggers the `greenhouse` environment, the traversal to the `greenhouse` directory, and the execution of the `python3 main.py` command:

``` bash
# TODO: Put the systemd file here
```

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