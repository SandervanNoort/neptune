#!/usr/bin/env python3
# -*-coding: utf-8-*-

"""The neptune class"""

from __future__ import (division, absolute_import, unicode_literals,
                        print_function)

import os
# Since these modules depend on the above variable, load after
from .system import System
from .local import Local

# do not import gtk by default
# from . indicator import Indicator

from . import tools


DBUS_SERVICE = "org.neptune.Service"
DBUS_INTERFACE = "org.neptune.Interface"
POLKIT_SERVICE = "org.neptune.service"
DBUS_PATH = "/Control"

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
ICON = os.path.join(ROOT, "icons", "neptune.svg")
CONFIG_DIR = os.path.join(ROOT, "config")

BACKLIGHT_DIR = "/sys/class/backlight"
BACKLIGHT_ORDER = ("acpi_video0",)
CPU_DIR = "/sys/devices/system/cpu"
SCREEN_OFF = "xset dpms force off"

BATTERIES = {
    "/sys/class/power_supply/BAT0/uevent": {
        "POWER_SUPPLY_CHARGE_NOW": "capacity",
        "POWER_SUPPLY_CURRENT_NOW": "rate",
        "POWER_SUPPLY_VOLTAGE_NOW": "voltage",
        "POWER_SUPPLY_STATUS": "state"},
    "/sys/class/power_supply/BAT1/uevent": {
        "POWER_SUPPLY_CHARGE_NOW": "capacity",
        "POWER_SUPPLY_CURRENT_NOW": "rate",
        "POWER_SUPPLY_VOLTAGE_NOW": "voltage",
        "POWER_SUPPLY_STATUS": "state"},
    "/proc/acpi/battery/BAT0/state": {
        "present rate": "rate",
        "remaining capacity": "capacity",
        "present voltage": "voltage",
        "charging state": "state"}}
BATTERY_INFO = "/proc/acpi/battery/BAT0/info"

AUTHOR = "Sander van Noort"
EMAIL = "Sander.van.Noort@gmail.com"
COPYRIGHT = "(C) 2011 Sander van Noort <Sander.van.Noort@gmail.com>"
NAME = "Neptune Indicator"
VERSION = "0.2"
DESCRIPTION = """Control the power consumption, brightness and input devices"""

APP_DIR = "/usr/share/applications"
AUTOSTART_DIR = os.path.join(os.path.expanduser("~"), ".config", "autostart")


class Error(Exception):
    """Error class for caught errors"""
    def __init__(self, value):
        # (__init__ from base not called) pylint: disable=W0231
        self.value = value

    def __str__(self):
        return self.value
