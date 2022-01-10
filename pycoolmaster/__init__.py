"""Module to communicate with CoolMaster over RS232"""
#!/usr/bin/env python3
import re
import serial
import time

__author__ = "Issac Goldstand"
__copyright__ = "Copyright 2020 Issac Goldstand"


_SWING_CHAR_TO_NAME = {
    "-": None,
    "0": None,
    "a": "auto",
    "h": "horizontal",
    "3": "30",
    "4": "45",
    "6": "60",
    "v": "vertical",
}

_SWING_NAME_TO_CHAR = {
    "auto": "a",
    "horizontal": "h",
    "30": "3",
    "45": "4",
    "60": "6",
    "vertical": "v",
}

_FAN_SPEEDS = ["low", "med", "high", "auto", "top"]
_MODES = ["auto", "cool", "dry", "fan", "heat"]


def autoupdate_property(func):
    def update_and_get(*args):
        args[0]._update_if_needed()
        return func(*args)

    return property(update_and_get)


class CoolMaster(object):
    def __init__(self, port, baud=9600, read_timeout=5, auto_update=True):
        """Initialize this CoolMaster instance to connect to a particular
        RS232 port at a particular baud."""
        self._port = port
        # Baud could have been overridden via "set baud" command...
        self._baud = baud
        self._read_timeout = read_timeout
        self._auto_update = auto_update
        self._ser = None
    
    def __del__(self):
        """Close the RS232 port (if open)"""
        if self._ser is not None:
            try:
                self._ser.close()
            except serial.serialutil.SerialException:
                pass 

    def _open(self):
        """Lazy connect the RS232 port"""
        if self._ser is None:
            self._ser = serial.Serial(self._port, self._baud, timeout = self._read_timeout)

        try:
            self._ser.open()
        except serial.serialutil.SerialException:
            pass    

    def _make_request(self, request):
        """Send a request to the CoolMaster and returns the response."""
        self._open()

        try:
            self._ser.write(b"\r\n")
            if self._ser.read_until(b">") != b"\r\n>":
                raise Exception("CoolMaster prompt not found")

            request = request + "\r\n"
            self._ser.write(request.encode("ascii"))
            # Echoed text
            self._ser.read_until(request.encode("ascii"))
            # Response
            response = self._ser.read_until(b"\r\n>")
            response = response.decode("ascii")

            if response.endswith("\r\n>"):
                response = response[:-1]

            if response.endswith("OK\r\n"):
                response = response[:-4]

            return response
        finally:
            self._ser.close()

    def devices(self):
        """Return a list of CoolMasterDevice objects representing the
        devices attached to the bridge."""
        status_lines = self._make_request("stat2").strip().split("\r\n")
        return [
            CoolMasterDevice(self, line[0:3], self._auto_update)
            for line in status_lines
        ]

    def info(self):
        """Get the general info the this CoolMaster."""
        lines = self._make_request("set").strip().split("\r\n")
        key_values = [re.split(r"\s*:\s*", line, 1) for line in lines]
        return dict(key_values)

class CoolMasterDevice(object):
    """A device attached to a CoolMaster bridge.

    This object caches data for 1 second so that reading a bunch of its
    properties in rapid succession doesn't require repeated server
    requests."""

    def __init__(self, bridge, uid, auto_update=True):
        """Initialize a new device given its unit identifier."""
        self._bridge = bridge
        self._uid = uid
        self._last_refresh_time = 0
        self._auto_update = auto_update

    def _update_if_needed(self):
        """Check whether the existing status is too stale and update it if so."""
        if self._auto_update and time.time() - self._last_refresh_time >= 1:
            self._update_status()

    def _update_status(self):
        """Fetch the device's current status from the bridge."""
        status_line = self._bridge._make_request("stat2 " + self._uid)

        # Status line looks like
        # 101 OFF 32C 04,93C Low  Dry  OK 1
        fields = re.split(r"\s+", status_line.strip())
        if len(fields) != 8:
            raise Exception("Unexpected status line format: " + str(fields))

        self._is_on = fields[1] == "ON"
        self._unit = "imperial" if fields[2][-1] == "F" else "celsius"
        self._thermostat = float(fields[2][:-1])
        self._temperature = float(fields[3][:-1].replace(",","."))
        self._fan_speed = fields[4].lower()
        self._mode = fields[5].lower()

        swing_line = self._bridge._make_request("query {} s".format(self._uid))
        self._swing_mode = None
        if swing_line != "":
            self._swing_mode = _SWING_CHAR_TO_NAME[swing_line.strip()]

        self._last_refresh_time = time.time()

    def _clear_status(self):
        """Force the next property read to refresh the device status if
        autoupdate mode is active."""
        self._last_refresh_time = 0

    def _make_request(self, format_str):
        """Make a request to the bridge. "UID" in format_str is replaced with
        device's unit ID."""
        return self._bridge._make_request(format_str.replace("UID", self._uid))

    def set_fan_speed(self, value):
        self._make_request("fspeed UID {}".format(value))
        self._clear_status()

    def set_mode(self, value):
        if value in _MODES:
            self._make_request(value + " UID")
            self._clear_status()
        else:
            raise ValueError(
                "Unrecognized mode {}. Valid values: {}".format(value, " ".join(_MODES))
            )

    def set_thermostat(self, value):
        self._make_request("temp UID {}".format(value))
        self._clear_status()

    def set_swing(self, value):
        if value in _SWING_NAME_TO_CHAR:
            self._make_request("swing UID {}".format(_SWING_NAME_TO_CHAR[value]))
            self._clear_status()
        else:
            raise ValueError(
                "Unrecognized swing mode {}. Valid values: {}".format(
                    value, " ".join(_SWING_NAME_TO_CHAR.keys())
                )
            )

    def turn_on(self):
        """Turn the device on."""
        self._make_request("on UID")
        self._clear_status()

    def turn_off(self):
        """Turn the device off."""
        self._make_request("off UID")
        self._clear_status()

    def update_status(self):
        """Force a status update. Normally, status is queried automatically
        if it hasn't been updated in the past second."""
        self._clear_status()
        self._update_status()

    @autoupdate_property
    def fan_speed(self):
        return self._fan_speed

    @autoupdate_property
    def is_on(self):
        return self._is_on

    @autoupdate_property
    def mode(self):
        return self._mode

    @autoupdate_property
    def status(self):
        return {
            "fan_speed": self._fan_speed,
            "is_on": self._is_on,
            "mode": self._mode,
            "swing": self._swing_mode,
            "temperature": self._temperature,
            "thermostat": self._thermostat,
            "uid": self._uid,
            "unit": self._unit,
        }

    @autoupdate_property
    def swing(self):
        return self._swing_mode

    @autoupdate_property
    def temperature(self):
        return self._temperature

    @autoupdate_property
    def thermostat(self):
        return self._thermostat

    @property
    def uid(self):
        return self._uid

    @autoupdate_property
    def unit(self):
        return self._unit
