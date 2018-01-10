#!/usr/bin/env python3
# -*-coding: utf-8-*-

"""Controling kernel parameters in /sys and /proc"""

from __future__ import (division, absolute_import, unicode_literals,
                        print_function)

import os
import re
import configobj
import collections
import six

import neptune


class System(object):
    """All control commands"""

    def __init__(self):
        self.values = collections.defaultdict(list)
        self.backlight = self.get_backlight()

        self.capacity_low = 0
        self.battery = None
        self.init_battery()

        self.init_cpu()

        self.kernel = {}
        self.init_power()

    @staticmethod
    def get_backlight():
        """Init the backlight settings"""

        backlights = {}
        if not os.path.exists(neptune.BACKLIGHT_DIR):
            return {}

        for backlight in os.listdir(neptune.BACKLIGHT_DIR):
            path = os.path.join(neptune.BACKLIGHT_DIR, backlight)
            try:
                with open(os.path.join(path, "max_brightness"), "r") as fobj:
                    max_brightness = int(fobj.read())
                    if max_brightness > 0:
                        min_brightness = max_brightness // 50
                        backlights[backlight] = {
                            "path": path,
                            "max": max_brightness,
                            "min": min_brightness
                        }
            except IOError:
                pass

        # Set default brightness
        for backlight in neptune.BACKLIGHT_ORDER:
            if backlight in backlights:
                backlights["default"] = backlights[backlight]
        if "default" not in backlights:
            backlights["default"] = next(six.itervalues(backlights))
        return backlights

    def init_battery(self):
        """Init the battery settings"""
        for battery in neptune.BATTERIES.keys():
            if os.path.exists(battery):
                self.battery = battery
                break

        try:
            with open(neptune.BATTERY_INFO, "r") as fobj:
                self.capacity_low = int(
                    re.search(r"design capacity low: *(\d*) .*",
                              fobj.read()).groups()[0])
        except (IOError, AttributeError):
            pass

    def init_cpu(self):
        """Init the CPU setting"""
        try:
            self.values["cpu_no"] = [
                cpu_no for cpu_no in os.listdir(neptune.CPU_DIR)
                if re.match(r"cpu\d+", cpu_no)]
        except OSError:
            pass

        try:
            fname = os.path.join(
                neptune.CPU_DIR, "cpu0", "cpufreq",
                "scaling_available_governors")
            with open(fname, "r") as fobj:
                governors = fobj.read().strip()
                if governors != "":
                    self.values["cpu"] = governors.split(" ")
        except IOError:
            pass

    def init_power(self):
        """Init the power settings"""
        self.kernel = {}
        config = configobj.ConfigObj(
            os.path.join(neptune.CONFIG_DIR, "kernel.ini"))
        for fname, options in config.items():
            for power in options:
                if not isinstance(options[power], list):
                    options[power] = [options[power]]
            if "/*/" in fname:
                dirname, search = fname.split("/*/")
                if os.path.exists(dirname):
                    for subdir in os.listdir(dirname):
                        fname2 = os.path.join(dirname, subdir, search)
                        if os.path.exists(fname2):
                            self.kernel[fname2] = options
            elif os.path.exists(fname):
                self.kernel[fname] = options

        self.values["power"] = list(set([
            power for options in self.kernel.values()
            for power in options.keys()]))

    def test_available(self, setting, value):
        """Test if the key is available"""
        if value not in self.values[setting]:
            raise neptune.Error(
                ("Unknown {setting} setting: {value}\n" +
                 "Available: {values}").format(
                     setting=setting,
                     value=value,
                     values=", ".join(self.values[setting])))

    def get_brightness(self, backlight="default"):
        """Get the current brightness"""
        try:
            with open(os.path.join(self.backlight[backlight]["path"],
                                   "actual_brightness"), "r") as fobj:
                return int(fobj.read().strip())
        except IOError:
            raise neptune.Error(
                "Backlight control unreadable: {0}".format(backlight))

    def set_brightness(self, brightness, backlight="default"):
        """Set the brightness"""
        if brightness == "max":
            brightness = self.backlight[backlight]["max"]
        if brightness == "min":
            brightness = self.backlight[backlight]["min"]

        if brightness == self.get_brightness(backlight):
            return

        try:
            fname = os.path.join(self.backlight[backlight]["path"],
                                 "brightness")
            with open(fname, "w") as fobj:
                fobj.write("{0}".format(brightness))
        except IOError:
            raise neptune.Error("Backlight unwritable: {0}".format(backlight))

    def update_brightness(self, change, backlight="default"):
        """Change the brightness"""
        try:
            self.set_brightness(self.get_brightness(backlight) + change,
                                backlight)
        except neptune.Error:
            pass

    def get_battery_proc(self):
        """Read acpi battery from /proc"""
        battery = {}
        try:
            with open(self.battery, "r") as fobj:
                for line in fobj:
                    result = re.search(r"(.*): *(\d*) (.*)", line)
                    if result:
                        key, value, units = result.groups()
                        if value == "":
                            value = units.lower()
                        else:
                            value = int(value)
                        if key in neptune.BATTERIES[self.battery]:
                            battery[neptune.BATTERIES[self.battery][key]] \
                                = value
        except IOError:
            print("Cannot read battery", self.battery)
        return battery

    def get_battery_sys(self):
        """Read acpi battery from /proc"""
        battery = {}
        try:
            with open(self.battery, "r") as fobj:
                for line in fobj:
                    result = re.search("(.*)=(.*)", line)
                    if result:
                        key, value = result.groups()
                        value = value.lower()
                        try:
                            value = int(value) // 1000
                        except ValueError:
                            pass
                        if key in neptune.BATTERIES[self.battery]:
                            battery[neptune.BATTERIES[self.battery][key]] \
                                = value
        except IOError:
            print("Cannot open battery {0}".format(self.battery))
        return battery

    def get_battery(self):
        """Get the current battery status"""
        if not self.battery:
            return {}
        if self.battery.startswith("/proc"):
            battery = self.get_battery_proc()
        elif self.battery.startswith("/sys"):
            battery = self.get_battery_sys()
        else:
            return {}

        if battery["state"] == "discharging" and battery["rate"] > 0:
            battery["watts"] = (battery["voltage"] / 1000 *
                                battery["rate"] / 1000)
            battery["timeleft"] = ((battery["capacity"] - self.capacity_low) /
                                   battery["rate"])
        return battery

    def get_cpu(self):
        """Get the current governor"""
        cpu_set = set()
        for cpu_no in self.values["cpu_no"]:
            try:
                fname = os.path.join(
                    neptune.CPU_DIR, cpu_no, "cpufreq", "scaling_governor")
                with open(fname, "r") as fobj:
                    cpu_set.add(fobj.read().strip())
            except IOError:
                pass
        if len(cpu_set) == 0:
            raise neptune.Error("CPU governors not available")
        elif len(cpu_set) == 1:
            return cpu_set.pop()
        else:
            return "mixed"

    def set_cpu(self, cpu):
        """Set the CPU governor"""
        self.test_available("cpu", cpu)
        if cpu != self.get_cpu():
            try:
                for cpu_no in self.values["cpu_no"]:
                    fname = os.path.join(
                        neptune.CPU_DIR, cpu_no, "cpufreq", "scaling_governor")
                    with open(fname, "w") as fobj:
                        fobj.write("{0}".format(cpu))
            except IOError:
                raise neptune.Error("Cannot set cpu to {0}".format(cpu))

    def get_power(self):
        """Get the current power state"""
        power_set = set(self.values["power"])
        for _fname, options in self._get_current_kernel():
            for power in power_set.copy():
                if (power in options and options["current"] is not None and
                        options["current"] not in options[power]):
                    power_set.remove(power)

        if len(power_set) == 1:
            return power_set.pop()
        else:
            return "mixed"

    def set_power(self, power):
        """Set the power state"""
        self.test_available("power", power)
        if power != self.get_power():
            for fname, options in self._get_current_kernel():
                if power in options \
                        and options["current"] not in options[power]:
                    try:
                        with open(fname, "w") as fobj:
                            fobj.write("{0}".format(options[power][0]))
                    except IOError:
                        print("Cannot write", fname, options[power][0])

    def _get_current_kernel(self):
        """Get current kernel settings"""
        for fname, options in self.kernel.items():
            try:
                with open(fname, "r") as fobj:
                    options["current"] = fobj.read().strip()
            except IOError:
                options["current"] = None
            yield fname, options
