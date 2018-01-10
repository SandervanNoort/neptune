#!/usr/bin/python3
# -*-coding: utf-8-*-

"""Neptune command-line"""

from __future__ import division, absolute_import, unicode_literals
from __future__ import print_function

import argparse
import sys
import dbus

import neptune

parser = argparse.ArgumentParser()
parser.add_argument("--get-cpu", action="store_true", default=False)
parser.add_argument("--get-battery", action="store_true", default=False)
parser.add_argument("--set-cpu", action="store", dest="cpu")
parser.add_argument("--get-power", action="store_true", default=False)
parser.add_argument("--set-power", action="store", dest="power")
parser.add_argument("--get-brightness", action="store_true", default=False)
parser.add_argument("--set-brightness", action="store", dest="brightness")
parser.add_argument("--screen-off", action="store_true", default=False)
parser.add_argument("--quit", action="store_true", default=False)
result = parser.parse_args()

try:
    bus = dbus.SystemBus()
    if result.quit:
        if bus.name_has_owner(neptune.DBUS_SERVICE):
            remote_object = bus.get_object(neptune.DBUS_SERVICE,
                                           neptune.DBUS_PATH)
            iface = dbus.Interface(remote_object, neptune.DBUS_INTERFACE)
            msg = "Neptune service stopped"
            iface.emit_info(msg, "")
            iface.exit()
            sys.exit(msg)
        else:
            sys.exit("Neptune service not running")

    local = neptune.Local()
    remote_object = bus.get_object(neptune.DBUS_SERVICE, neptune.DBUS_PATH)
    iface = dbus.Interface(remote_object, neptune.DBUS_INTERFACE)

    if result.cpu:
        iface.set_cpu(result.cpu)
        msg = "CPU set to {0}".format(iface.get_cpu())
        iface.emit_info(msg, "")
        print(msg)
    if result.get_cpu:
        print("Current CPU: {0}".format(iface.get_cpu()))

    if result.power:
        iface.set_power(result.power)
        msg = "Power set to {0}".format(iface.get_power())
        iface.emit_info(msg, "")
        print(msg)
    if result.get_power:
        print("Current power setting: {0}".format(iface.get_power()))

    if result.brightness:
        iface.set_brightness(result.brightness, "default")
        msg = "Brightness set to {0}".format(iface.get_brightness("default"))
        iface.emit_info(msg, "")
        print(msg)
    if result.get_brightness:
        print("Current brightness: {0}".format(
            iface.get_brightness("default")))

    if result.screen_off:
        local.screen_off()

    if result.get_battery:
        print("Battery:")
        for key, value in iface.get_battery().items():
            print("   {0}: {1}".format(key, value))

except dbus.DBusException as error:
    sys.exit(error)
