#!/usr/bin/env python3
# -*-coding: utf-8-*-

"""Fix RadioMenuItem"""

from __future__ import (division, absolute_import, unicode_literals,
                        print_function)

from gi.repository import Gtk
from gi.importer import modules


def fix_gtk():
    """Fix Gtk.RadioMenuItem
    - To have a label for Gtk.MenuItem, require label=args
    - Let Gtk.RadioMenuItem to have group=None argument
    """
    # (access to protected member) pylint: disable=W0212
    Gtk.MenuItem = modules["Gtk"]._introspection_module.MenuItem
    # pylint: enable=W0212

    class RadioMenuItem(Gtk.RadioMenuItem):
        """RadioMenuItem accepts the group=argument"""
        # (too many public methods) pylint: disable=R0904
        def __init__(self, label=None, group=None):
            if group:
                super(RadioMenuItem, self).__init__(label=label, group=group)
            else:
                super(RadioMenuItem, self).__init__(label=label)
    Gtk.RadioMenuItem = RadioMenuItem
