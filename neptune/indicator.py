#!/usr/bin/env python3
# -*-coding: utf-8-*-

"""Indicator"""

from __future__ import (division, absolute_import, unicode_literals,
                        print_function)

import dbus

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Notify
from gi.repository import AppIndicator3

# Fixing Gtk.RadioMenuItem
# from .gtk3 import fix_gtk
# fix_gtk()

import neptune

MIN_BRIGHTNESS = 10


class Indicator(object):
    """Neptune indicator"""

    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new(
            "neptune", neptune.ICON,
            AppIndicator3.IndicatorCategory.HARDWARE)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.connect("scroll-event", self.scroll)

        Notify.init("Neptune")

        self.local = neptune.Local()
        self.iface = None
        self.dbus_connect()

        menu = Gtk.Menu()

        item = Gtk.MenuItem(label="Screen")
        item.set_submenu(ScreenMenu(self))
        item.show()
        menu.append(item)

        item = Gtk.MenuItem(label="Power")
        item.set_submenu(PowerMenu(self))
        item.show()
        menu.append(item)

        item = Gtk.MenuItem(label="Input devices")
        item.set_submenu(XInputMenu(self))
        item.show()
        menu.append(item)

        item = Gtk.SeparatorMenuItem()
        item.show()
        menu.append(item)

        item = Gtk.MenuItem(label="Config")
        item.set_submenu(ConfigMenu(self))
        item.show()
        menu.append(item)

        item = Gtk.MenuItem(label="About")
        item.connect("activate", self.about)
        item.show()
        menu.append(item)

        item = Gtk.MenuItem(label="Exit")
        item.connect("activate", self.quit)
        item.show()
        menu.append(item)

        self.indicator.set_menu(menu)

    def dbus_exec(self, function, args, default="", first=True):
        """Try a dbus function"""
        try:
            return getattr(self.iface, function)(*args)
        except dbus.DBusException as error:
            if first and error.get_dbus_name() \
                    == "org.freedesktop.DBus.Error.ServiceUnknown":
                self.dbus_connect()
                return self.dbus_exec(function, args, default, False)
            else:
                if default == "GTK":
                    dialog = Gtk.MessageDialog(
                        buttons=Gtk.ButtonsType.CLOSE,
                        message_type=Gtk.MessageType.WARNING,
                        text=error)
                    dialog.run()
                    dialog.destroy()
                else:
                    return default

    def dbus_connect(self):
        """Connect to dbus"""
        try:
            bus = dbus.SystemBus()
            remote_object = bus.get_object(neptune.DBUS_SERVICE,
                                           neptune.DBUS_PATH)
            self.iface = dbus.Interface(remote_object, neptune.DBUS_INTERFACE)
            self.iface.connect_to_signal("info", self.info)
            self.iface.test()
        except dbus.DBusException as error:
            dialog = Gtk.MessageDialog(
                buttons=Gtk.ButtonsType.CLOSE,
                message_type=Gtk.MessageType.WARNING,
                text="Cannot connect to Neptune server")
            print(error)
            dialog.run()
            dialog.destroy()

    @staticmethod
    def info(title, message):
        """Notification"""
        notification = Notify.Notification.new(title, message, neptune.ICON)
        notification.show()

    def scroll(self, _widget, _mouse, direction):
        """Scrolled on menu"""
        if direction == 0:  # scroll up
            self.dbus_exec("update_brightness", (+1, "default"))
        elif direction == 1:  # scroll down
            self.dbus_exec("update_brightness", (-1, "default"))

    @staticmethod
    def quit(_widget):
        """Quit"""
        Gtk.main_quit()

    @staticmethod
    def about(_widget):
        """About dialog"""
        dialog = Gtk.AboutDialog()
        dialog.set_program_name(neptune.NAME)
        dialog.set_version(neptune.VERSION)
        dialog.set_copyright(neptune.COPYRIGHT)
        dialog.set_comments(neptune.DESCRIPTION)
        if "." in neptune.ICON:
            dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(neptune.ICON))
        else:
            dialog.set_logo_icon_name(neptune.ICON)
        dialog.connect("response", lambda widget, event: dialog.destroy())
        dialog.show()


class BrightnessMenu(Gtk.Menu):
    """Submenu with brightness settings"""
    # (too many public methods) pylint: disable=R0904

    def __init__(self, main, backlight):
        super(BrightnessMenu, self).__init__()
        self.main = main
        self.backlight = backlight

        reference = None
        max_brightness = self.main.dbus_exec("get_max_brightness",
                                             (backlight,), [])
        min_brightness = self.main.dbus_exec("get_min_brightness",
                                             (backlight,), [])
        for brightness in (
                list(range(min_brightness, max_brightness,
                           int((max_brightness - min_brightness) / 10))) +
                [max_brightness]):
            item = Gtk.RadioMenuItem(group=reference, label=brightness)
            item.brightness = brightness
            reference = item
            item.connect("activate", self.set_brightness, brightness)
            self.append(item)
            item.show()

        self.connect("show", self.update)

    def update(self, _widget):
        """Update menu to pre-select brightness brightness"""
        brightness = self.main.dbus_exec("get_brightness", (self.backlight,),
                                         None)
        for item in self.get_children():
            if hasattr(item, "brightness") and item.brightness == brightness:
                item.set_active(True)

    def set_brightness(self, widget, brightness):
        """Set the brightness"""
        if widget.get_active():
            self.main.dbus_exec("set_brightness", (brightness, self.backlight))


class ScreenMenu(Gtk.Menu):
    """Submenu with screen settings"""
    # (too many public methods) pylint: disable=R0904

    def __init__(self, main):
        super(ScreenMenu, self).__init__()
        self.main = main

        backlights = main.dbus_exec("get_backlights", [])
        if len(backlights) > 0:
            self.max_brightness = main.dbus_exec("get_max_brightness",
                                                 ("default",), [])
            self.min_brightness = main.dbus_exec("get_min_brightness",
                                                 ("default",), [])

            reference = None
            item = Gtk.RadioMenuItem(
                group=reference,
                label="Maximum brightness: {0}".format(self.max_brightness))
            reference = item
            item.screen = self.max_brightness
            item.connect("activate", self.set_brightness, self.max_brightness)
            self.append(item)
            item.show()

            item = Gtk.RadioMenuItem(group=reference,
                                     label="Current brightness: ...")
            reference = item
            item.screen = "mixed"
            self.append(item)
            item.hide()

            item = Gtk.RadioMenuItem(
                group=reference,
                label="Minimum brightness: {0}".format(self.min_brightness))
            reference = item
            item.screen = self.min_brightness
            item.connect("activate", self.set_brightness, self.min_brightness)
            self.append(item)
            item.show()
        else:
            self.min_brightness = None
            self.max_brightness = None

        item = Gtk.MenuItem(label="Screen off")
        item.connect("activate", self.screen_off)
        self.append(item)
        item.show()

        backlights = main.dbus_exec("get_backlights", [])
        if len(backlights) > 0:
            item = Gtk.MenuItem(label="Brightness")
            item.set_submenu(BrightnessMenu(main, "default"))
            item.show()
            self.append(item)

        if len(backlights) > 2:
            item = Gtk.SeparatorMenuItem()
            item.show()
            self.append(item)

            for backlight in backlights:
                if backlight == "default":
                    continue
                item = Gtk.MenuItem(label="Alternative ({0})".format(
                    backlight))
                item.set_submenu(BrightnessMenu(main, backlight))
                item.show()
                self.append(item)

        self.connect("show", self.update)

    def update(self, _widget):
        """Update menu to pre-select brightness brightness"""
        brightness = self.main.dbus_exec("get_brightness", ("default",), None)
        for item in self.get_children():
            if hasattr(item, "screen") and item.screen == brightness:
                item.set_active(True)
            elif hasattr(item, "screen") and item.screen == "mixed":
                if brightness not in (self.min_brightness,
                                      self.max_brightness):
                    item.set_label("Current brightness: {0}".format(
                        brightness))
                    item.set_active(True)
                    item.show()
                else:
                    item.hide()

    def set_brightness(self, widget, brightness):
        """Set the brightness"""
        if widget.get_active():
            self.main.dbus_exec("set_brightness", (brightness, "default"))

    def screen_off(self, _widget):
        """Screenoff clicked in menu"""
        self.main.local.screen_off()


class ConfigMenu(Gtk.Menu):
    """Configuration menu"""
    # (too many public methods) pylint: disable=R0904

    def __init__(self, main):
        super(ConfigMenu, self).__init__()
        self.main = main

        item = Gtk.CheckMenuItem(label="Autostart")
        item.connect("activate", self.set_autostart)
        self.append(item)
        item.show()

        self.connect("show", self.update)

    def update(self, _widget):
        """Update the menu items"""
        for item in self.get_children():
            if item.get_label() == "Autostart":
                item.set_active(self.main.local.get_autostart())

    def set_autostart(self, widget):
        """Autostart clicked in menu"""
        self.main.local.set_autostart(widget.get_active())


class PowerMenu(Gtk.Menu):
    """Menu with power options"""
    # (too many public methods) pylint: disable=R0904

    def __init__(self, main):
        super(PowerMenu, self).__init__()
        self.main = main

        reference = None
        for power in main.dbus_exec("get_values", ("power",), []):
            item = Gtk.RadioMenuItem(group=reference,
                                     label=power.capitalize())
            item.connect("activate", self.set_power, power)
            item.power = power
            reference = item
            self.append(item)
            item.show()

        item = Gtk.RadioMenuItem(group=reference, label="Mixed")
        item.connect("toggled",
                     lambda w: w.show() if w.get_active() else w.hide())
        item.power = "mixed"
        self.append(item)
        item.hide()

        item = Gtk.SeparatorMenuItem()
        self.append(item)
        item.show()

        item = Gtk.MenuItem(label="CPU")
        item.set_submenu(CpuMenu(main))
        item.show()
        self.append(item)

        item = Gtk.SeparatorMenuItem()
        self.append(item)
        item.show()

        item = Gtk.MenuItem(label="Capacity: calculating...")
        item.capacity = True
        self.append(item)
        item.show()

        item = Gtk.MenuItem(label="Power: calculating...")
        item.watts = True
        self.append(item)
        item.show()

        self.connect("show", self.update)

    def update(self, _widget):
        """Update the power menu"""

        self.update_power()
        self.update_battery()

    def update_battery(self):
        """Update battery status in the menu"""
        battery = self.main.dbus_exec("get_battery", (), {})
        for item in self.get_children():
            if hasattr(item, "capacity"):
                if "capacity" in battery:
                    item.set_label("Capacity: {0} mAh".format(
                        battery["capacity"]))
                else:
                    item.hide()
            elif hasattr(item, "watts"):
                if "state" in battery:
                    if battery["state"] == "discharging":
                        if "watts" in battery:
                            item.set_label(
                                ("Power: {watt:.1f} W" +
                                 " ({hour:d}:{mins:02d} hours)").format(
                                     watt=float(battery["watts"]),
                                     hour=int(float(battery["timeleft"]) // 1),
                                     mins=int(
                                         60 * float(battery["timeleft"]) % 1)))
                        else:
                            item.set_label("On battery")
                    else:
                        item.set_label("On AC Power")
                else:
                    item.hide()

    def update_power(self):
        """Update power status in the menu"""
        power = self.main.dbus_exec("get_power", (), None)
        for item in self.get_children():
            if hasattr(item, "power") and item.power == power:
                item.set_active(True)

    def set_power(self, widget, power):
        """Set the CPU governor"""
        if widget.get_active():
            self.main.dbus_exec("set_power", (power,))


class CpuMenu(Gtk.Menu):
    """Submenu with CPU options"""
    # (too many public methods) pylint: disable=R0904

    def __init__(self, main):
        super(CpuMenu, self).__init__()
        self.main = main

        reference = None
        for governor in main.dbus_exec("get_values", ("cpu",), []):
            item = Gtk.RadioMenuItem(group=reference,
                                     label=governor.capitalize())
            item.cpu = governor
            reference = item
            item.connect("activate", self.set_cpu, governor)
            self.append(item)
            item.show()

        item = Gtk.RadioMenuItem(group=reference, label="Mixed")
        item.cpu = "mixed"
        item.connect("toggled",
                     lambda w: w.show() if w.get_active() else w.hide())
        self.append(item)
        item.hide()

        self.connect("show", self.update)

    def update(self, widget):
        """Update menu to pre-select current cpu governor"""
        cpu = self.main.dbus_exec("get_cpu", (), None)
        for item in widget.get_children():
            if item.cpu == cpu:
                item.set_active(True)

    def set_cpu(self, widget, cpu):
        """Set the CPU governor"""
        if widget.get_active():
            self.main.dbus_exec("set_cpu", (cpu,))


class XInputMenu(Gtk.Menu):
    """Menu for main classes of xinput (pointer and keyboard)"""
    # (too many public methods) pylint: disable=R0904

    def __init__(self, main):
        super(XInputMenu, self).__init__()
        self.main = main

        #  menu.connect("show", update)
        for xname, xid, _xenabled in main.local.get_xinput_list(""):
            label = xname.replace("Virtual core", "").strip().capitalize()
            item = Gtk.MenuItem(label=label)
            item.set_submenu(XSlaveMenu(main, xid))
            item.show()
            self.add(item)


class XSlaveMenu(Gtk.Menu):
    """Menu with all the slave xinputs"""
    # (too many public methods) pylint: disable=R0904

    def __init__(self, main, master_id):
        super(XSlaveMenu, self).__init__()
        self.main = main
        self.master_id = master_id

        self.connect("show", self.update)

    def update(self, _widget):
        """Fill the xslave menu"""
        current = dict([(item.get_label(), item)
                        for item in self.get_children()])
        for xname, xid, xenabled in self.main.local.get_xinput_list(
                self.master_id):
            if "Virtual" in xname:
                continue
            xlabel = "{xname} ({xid})".format(xname=xname, xid=xid)
            if xlabel not in current.keys():
                item = Gtk.CheckMenuItem(label=xlabel)
                item.connect("activate", self.set_xinput, xid)
                item.set_active(xenabled)
                item.show()
                self.append(item)
            else:
                current[xlabel].set_active(xenabled)
                del current[xlabel]
        for item in current.values():
            item.destroy()

    def set_xinput(self, widget, xid):
        """Set the xinput"""
        self.main.local.set_xinput_enabled(xid, widget.get_active())
