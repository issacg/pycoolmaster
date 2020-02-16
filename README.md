pycoolmaster
===============
A Python 3 library for interacting with a [CoolMaster HVAC bridge](http://www.coolautomation.wiki/index.php?title=CoolMaster) using the older [(legacy) protocol](http://coolautomation.com/lib/doc/prm/HTML/CM_PRM/)



Installation
------------
`pip install pycoolmaster`

Usage
-----

```python

    from pycoolmaster import CoolMaster

    # Supply the serial port and optional baud rate (default 9600).
    #
    # By default, properties will be refreshed by querying the device
    # if last refresh was more than 1 second ago; pass auto_update=False
    # to disable that behavior (in which case you will need to call
    # update_status() explicitly).
    cool = CoolMaster('/dev/ttyUSB0', baud=19200, read_timeout=5, auto_update=True)

    # Returns a list of CoolMasterDevice objects
    devices = cool.devices()

    # Device's unit ID on the CoolMaster bridge, e.g., "102"
    device.uid

    # Temperature unit: imperial, celsius
    device.unit

    # Current reading of device's thermometer
    device.temperature

    # Current setting of device's thermostat
    device.thermostat
    device.set_thermostat(28)

    # True if device is turned on
    device.is_on
    device.turn_on()
    device.turn_off()

    # Fan speed: low, med, high, auto, top
    device.fan_speed
    device.set_fan_speed('auto')

    # Mode of operation: auto, cool, dry, fan, heat
    device.mode
    device.set_mode('cool')

    # Swing mode: horizontal, vertical, auto, 30, 45, 60
    # Numeric settings are degrees of louver tilt. On read, the property can
    # be None if the bridge reports that the device doesn't support swing.
    device.swing
    device.set_swing('30')

    # Dict with all the properties listed above
    device.status

    # Force refresh of status (by default, device auto-updates its status
    # if most recent update is more than 1 second ago)
    device.update_status()
```

Acknowledgements
-------
Thanks to @koreth for his [pycoolmasternet](https://github.com/koreth/pycoolmasternet) library which was used as a basis for this library!
