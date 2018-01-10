#!/usr/bin/env python3
# -*-coding: utf-8-*-

"""Neptune dbus daemon"""

from __future__ import division, absolute_import, unicode_literals

import dbus
import dbus.service
import dbus.mainloop.glib

import neptune.server

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    name = dbus.service.BusName(neptune.DBUS_SERVICE, bus)
    dbusobject = neptune.server.ControlObject(bus, neptune.DBUS_PATH)

    dbusobject.start()
