#!/usr/bin/env python3
# -*-coding: utf-8-*-

"""Run dbus system service"""

from __future__ import (division, absolute_import, unicode_literals,
                        print_function)

import dbus
import dbus.service
import dbus.mainloop.glib

import neptune
from .polkit_dbus import PolkitDBus

# class GeneralException(dbus.DBusException):
#     """General exception when error occurs"""
#     _dbus_error_name = ""


class ControlObject(PolkitDBus):
    """The DBus object"""
    # (too many public methods) pylint: disable=R0904
    # (interface not implemente) pylint: disable=R0923

    def __init__(self, conn=None, object_path=None, bus_name=None):
        PolkitDBus.__init__(self, conn, object_path, bus_name)
        self.system = neptune.System()

    @dbus.service.signal(neptune.DBUS_INTERFACE)
    def info(self, title, message):
        """Info signal"""
        # (method coud be function) pylint: disable=R0201

        print("Emited info:", message, title)

    @dbus.service.method(neptune.DBUS_INTERFACE)
    def test(self):
        """Simple test function"""
        # (method coud be function) pylint: disable=R0201

        return True

    @dbus.service.method(neptune.DBUS_INTERFACE)
    def emit_info(self, title, message):
        """Emit info signal"""
        self.info(title, message)

    @dbus.service.method(neptune.DBUS_INTERFACE)
    def get_brightness(self, backlight="default"):
        """Return brightness"""
        try:
            return self.system.get_brightness(backlight)
        except neptune.Error as error:
            raise dbus.DBusException(error)

    @dbus.service.method(neptune.DBUS_INTERFACE, sender_keyword="sender")
    def set_brightness(self, brightness, backlight="default", sender=None):
        """Return brightness"""
        self.check_polkit(sender, "{0}.control".format(neptune.POLKIT_SERVICE))
        try:
            self.system.set_brightness(brightness, backlight)
        except neptune.Error as error:
            raise dbus.DBusException(error)

    @dbus.service.method(neptune.DBUS_INTERFACE, sender_keyword="sender")
    def update_brightness(self, change, backlight="default", sender=None):
        """Return brightness"""
        self.check_polkit(sender, "{0}.control".format(neptune.POLKIT_SERVICE))
        try:
            self.system.update_brightness(change, backlight)
        except neptune.Error as error:
            raise dbus.DBusException(error)

    @dbus.service.method(neptune.DBUS_INTERFACE, out_signature='a{ss}')
    def get_battery(self):
        """Return battery settings"""
        try:
            battery = self.system.get_battery()
        except neptune.Error as error:
            raise dbus.DBusException(error)
        return dict(zip(battery.keys(),
                        [str(val) for val in battery.values()]))

    @dbus.service.method(neptune.DBUS_INTERFACE)
    def get_power(self):
        """Return power setting"""
        try:
            return self.system.get_power()
        except neptune.Error as error:
            raise dbus.DBusException(error)

    @dbus.service.method(neptune.DBUS_INTERFACE, sender_keyword="sender")
    def set_power(self, power, sender=None):
        """Return brightness"""
        self.check_polkit(sender, "{0}.control".format(neptune.POLKIT_SERVICE))
        try:
            self.system.set_power(power)
        except neptune.Error as error:
            raise dbus.DBusException(error)

    @dbus.service.method(neptune.DBUS_INTERFACE)
    def get_cpu(self):
        """Return power setting"""
        try:
            return self.system.get_cpu()
        except neptune.Error as error:
            raise dbus.DBusException(error)

    @dbus.service.method(neptune.DBUS_INTERFACE, sender_keyword="sender")
    def set_cpu(self, cpu, sender=None):
        """Return brightness"""
        self.check_polkit(sender, "{0}.control".format(neptune.POLKIT_SERVICE))
        try:
            self.system.set_cpu(cpu)
        except neptune.Error as error:
            raise dbus.DBusException(error)

    @dbus.service.method(neptune.DBUS_INTERFACE)
    def get_backlights(self):
        """Return the possible backlight operators"""
        return list(self.system.backlight.keys())
#         return [backlight for backlight in self.system.backlight.keys()
#                 if backlight != "default"]

    @dbus.service.method(neptune.DBUS_INTERFACE)
    def get_max_brightness(self, backlight):
        """Return the maximum available backlight"""
        return self.system.backlight[backlight]["max"]

    @dbus.service.method(neptune.DBUS_INTERFACE)
    def get_min_brightness(self, backlight):
        """Return the maximum available backlight"""
        return self.system.backlight[backlight]["min"]

    @dbus.service.method(neptune.DBUS_INTERFACE)
    def get_values(self, name):
        """Return power setting"""
        if name in self.system.values:
            values = self.system.values[name]
            if len(values) < 20:
                return values
            else:
                return [values[i] for i in range(
                    0, len(values),
                    int(len(values) / 20) + 1)] + [values[-1]]
        else:
            raise dbus.DBusException("No values for {0}".format(name))

    @dbus.service.method(neptune.DBUS_INTERFACE, sender_keyword='sender')
    def exit(self, sender=None):
        """Exit server process"""
        self.check_polkit(sender, "{0}.exit".format(neptune.POLKIT_SERVICE))
        self.stop()
