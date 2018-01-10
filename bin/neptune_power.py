#!/usr/bin/env python3
# -*-coding: utf-8-*-

"""Neptune script when battery state changes"""

from __future__ import (division, absolute_import, unicode_literals,
                        print_function)

import sys
import dbus

import neptune

try:
    bus = dbus.SystemBus()
    remote_object = bus.get_object(neptune.DBUS_SERVICE, neptune.DBUS_PATH)
    iface = dbus.Interface(remote_object, neptune.DBUS_INTERFACE)

    if len(sys.argv) == 2 and sys.argv[1] == "false":
        iface.set_power("performance")
        iface.emit_info("Power connected", "Now on performance mode")
    elif len(sys.argv) == 2 and sys.argv[1] == "true":
        iface.set_power("powersave")
        iface.emit_info("Power disconnected", "Now on powersave mode")
    else:
        print("Usage: neptune <true/false>")
except dbus.DBusException as error:
    sys.exit(error)
