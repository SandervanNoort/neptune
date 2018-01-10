#!/usr/bin/env python3
# -*-coding: utf-8-*-

"""Dbus system service with polkit authorization"""

from __future__ import (division, absolute_import, unicode_literals,
                        print_function)

from gi.repository import GObject
import dbus
import dbus.service
import dbus.mainloop.glib


class PermissionDeniedByPolicy(dbus.DBusException):
    """Exception when policykit denies"""
    _dbus_error_name = 'com.ubuntu.DeviceDriver.PermissionDeniedByPolicy'


class PolkitDBus(dbus.service.Object):
    """The DBus object"""

    def __init__(self, conn=None, object_path=None, bus_name=None):
        dbus.service.Object.__init__(self, conn, object_path, bus_name)

        # the following variables are used by check_polkit
        self.polkit = None
        self.enforce_polkit = True
        self.dbus_info = dbus.Interface(
            conn.get_object('org.freedesktop.DBus',
                            '/org/freedesktop/DBus/Bus', False),
            'org.freedesktop.DBus')

        self.mainloop = None

    def start(self):
        """Start a mainloop"""
        self.mainloop = GObject.MainLoop()
        self.mainloop.run()

    def stop(self):
        """Stop a mainloop"""
        if self.mainloop:
            self.mainloop.quit()

    def check_polkit(self, sender, privilege):
        """Verify that sender has a given PolicyKit privilege.
        sender: sender's (private) D-BUS name, such as ":1:42"
                (sender_keyword in @dbus.service.methods)
        privilege: PolicyKit privilege string.

        This method returns if the caller is privileged, and otherwise throws a
        PermissionDeniedByPolicy exception.
        """
        if sender is None:
            # called locally, not through D-BUS
            return

        # get peer PID
        pid = self.dbus_info.GetConnectionUnixProcessID(sender)

        # query PolicyKit
        if self.polkit is None:
            self.polkit = dbus.Interface(
                dbus.SystemBus().get_object(
                    "org.freedesktop.PolicyKit1",
                    "/org/freedesktop/PolicyKit1/Authority",
                    False),
                "org.freedesktop.PolicyKit1.Authority")

        try:
            # we don't need is_challenge return here,
            #    since we call with AllowUserInteraction
            (is_auth, _, _details) = self.polkit.CheckAuthorization(
                ('unix-process', {
                    'pid': dbus.UInt32(pid, variant_level=1),
                    'start-time': dbus.UInt64(0, variant_level=1)}),
                privilege, {'': ''}, dbus.UInt32(1), '', timeout=600)
        except dbus.DBusException as error:
            if error.get_dbus_name \
                    == 'org.freedesktop.DBus.Error.ServiceUnknown':
                # polkitd timed out, connect again
                self.polkit = None
                return self.check_polkit(sender, privilege)
            else:
                raise

        if not is_auth:
            raise PermissionDeniedByPolicy(privilege)
