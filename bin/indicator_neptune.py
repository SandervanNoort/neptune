#!/usr/bin/env python3
# -*-coding: utf-8-*-

"""Neptune indicator"""

from __future__ import division, absolute_import, unicode_literals

from gi.repository import Gtk
import signal
import dbus.mainloop.glib

import neptune.indicator

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # listen for ctrl-c
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)  # dbus signals
    neptune.indicator.Indicator()
    Gtk.main()
