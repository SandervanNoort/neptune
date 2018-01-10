#!/usr/bin/env python3
# -*-coding: utf-8-*-

"""Install script"""

from __future__ import division, absolute_import, unicode_literals

import sys
import os
import re

from distutils.core import setup
import distutils.command.build_py
import distutils.command.install_data
import distutils.command.install_scripts


def substitute(fname, values):
    """Substitute the variable declarations"""

    with open(os.path.join(fname), "r") as fobj:
        contents = fobj.read()
        for key, value in values.items():
            contents = re.sub("{0} *=.*".format(key),
                              "{0} = \"{1}\"".format(key, value),
                              contents)
    with open(os.path.join(fname), "w") as fobj:
        fobj.write(contents)


class build_py(distutils.command.build_py.build_py):
    """Install python modules"""
    # (invalid class name) pylint: disable=C0103
    # (too many public methods) pylint: disable=R0904

    def run(self):
        distutils.command.build_py.build_py.run(self)
        substitute(
            os.path.join(self.build_lib, "neptune/__init__.py"),
            {"DBUS_SERVICE": "org.neptune.Service",
             "DBUS_INTERFACE": "org.neptune.Interface",
             "POLKIT_SERVICE": "org.neptune.service",
             "CONFIG_DIR": "/etc/neptune",
             "ICON": "neptune"})


class install_data(distutils.command.install_data.install_data):
    """Install data files"""
    # (invalid class name) pylint: disable=C0103
    # (too many public methods) pylint: disable=R0904

    def run(self):
        renames = {"neptune_power.py": "neptune-power"}
        distutils.command.install_data.install_data.run(self)
        substitute(
            os.path.join(self.install_dir, "share", "dbus-1",
                         "system-services", "org.neptune.Service.service"),
            {"Exec": os.path.join(sys.prefix, "bin", "neptune-server")})
        for fullname in self.outfiles:
            fname = os.path.basename(fullname)
            dirname = os.path.dirname(fullname)
            if fname in renames:
                os.rename(fullname, os.path.join(dirname, renames[fname]))
            elif fname.endswith(".py"):
                os.rename(fullname, os.path.join(dirname, fname[:-3]))


class install_scripts(distutils.command.install_scripts.install_scripts):
    """Install scripts"""
    # (invalid class name) pylint: disable=C0103
    # (too many public methods) pylint: disable=R0904

    def run(self):
        renames = {"neptune_cmd.py": "neptune",
                   "indicator_neptune.py": "indicator-neptune",
                   "neptune_server.py": "neptune-server"}
        distutils.command.install_scripts.install_scripts.run(self)
        for fullname in self.outfiles:
            fname = os.path.basename(fullname)
            dirname = os.path.dirname(fullname)
            if fname in renames:
                os.rename(fullname, os.path.join(dirname, renames[fname]))
            elif fname.endswith(".py"):
                os.rename(fullname, os.path.join(dirname, fname[:-3]))

setup(
    name="neptune",
    packages=[str("neptune")],
    cmdclass={"build_py": build_py,
              "install_data": install_data,
              "install_scripts": install_scripts},
    version="0.2",
    description="Control brightness, power consumption and input devices",
    author="Sander van Noort",
    author_email="Sander.van.Noort@gmail.com",
    scripts=["bin/neptune_cmd.py",
             "bin/indicator_neptune.py",
             "bin/neptune_server.py"],
    data_files=[("/etc/neptune", ["config/kernel.ini"]),
        ("share/applications", ["neptune.desktop"]),
        ("share/icons/hicolor/scalable/apps", ["icons/neptune.svg"]),
        ("/etc/pm/power.d", ["bin/neptune_power.py"]),
        ("share/polkit-1/actions", ["dbus/org.neptune.service.policy"]),
        ("/etc/dbus-1/system.d", ["dbus/org.neptune.Service.conf"]),
        ("share/dbus-1/system-services", ["dbus/org.neptune.Service.service"]),
        ("share/doc/neptune", ["docs/jupiter-vs-neptune.txt"])]
    )
