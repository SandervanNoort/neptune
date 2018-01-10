#!/usr/bin/env python3
# -*-coding: utf-8-*-

"""Commands that have to be done by the local user"""

from __future__ import (division, absolute_import, unicode_literals,
                        print_function)

import re
import os
import subprocess
import logging

import neptune

from . import tools

logger = logging.getLogger(__name__)


class Local(object):
    """All control commands"""

    def __init__(self):
        pass

    @staticmethod
    def screen_off():
        """Turn off the screen"""
        try:
            subprocess.check_call(neptune.SCREEN_OFF, shell=True)
        except subprocess.CalledProcessError as error:
            logger.error(error)
            logger.error(tools.to_unicode(error.output))

    def get_xinput_list(self, master_id=""):
        """Get all xinput devices"""
        current_master = ""
        try:
            output = subprocess.check_output("xinput list", shell=True)
        except subprocess.CalledProcessError as error:
            logger.error(error)
            logger.error(tools.to_unicode(error.output))
            return
        output = tools.to_unicode(output)

        for line in output.split("\n"):
            result = re.match(r".*[\u21b3\u23a1\u23a3](.*)id=(\d+).*\[(.*)\]",
                              line)
            if result:
                xlabel, xid, xtype = [val.strip() for val in result.groups()]
                if "master" in xtype:
                    current_master = xid
                    if master_id == "":
                        yield xlabel, xid, self._get_xinput_enabled(xid)
                if "slave" in xtype and master_id == current_master:
                    yield xlabel, xid, self._get_xinput_enabled(xid)

    @staticmethod
    def _get_xinput_enabled(xid):
        """Get whether the device is enable"""
        pattern = re.compile(r".*\tDevice Enabled .*:\t(\d)")
        try:
            output = subprocess.check_output(
                "xinput --list-props {0}".format(xid),
                shell=True)
        except subprocess.CalledProcessError as error:
            logger.error(error)
            logger.error(tools.to_unicode(error.output))
            return False
        output = tools.to_unicode(output)

        for line in output.split("\n"):
            result = pattern.match(line)
            if result:
                return bool(int(result.groups()[0]))
        return False

    def set_xinput_enabled(self, xid, enabled):
        """Enable or disable the device"""
        if enabled != self._get_xinput_enabled(xid):
            cmd = "xinput set-prop {xid} 'Device Enabled' {enabled:d}".format(
                xid=xid, enabled=enabled)
            try:
                subprocess.check_call(cmd, shell=True)
            except subprocess.CalledProcessError as error:
                logger.error(error)
                logger.error(tools.to_unicode(error.output))

    @staticmethod
    def get_autostart():
        """Autostart is enabled"""
        return os.path.exists(
            os.path.join(neptune.AUTOSTART_DIR, "neptune.desktop"))

    @staticmethod
    def set_autostart(enabled):
        """Set autostart to <set_on>"""

        desktop_autostart = os.path.join(neptune.AUTOSTART_DIR,
                                         "neptune.desktop")
        desktop_global = os.path.join(neptune.APP_DIR, "neptune.desktop")
        if not os.path.exists(desktop_global):
            desktop_global = os.path.join(neptune.ROOT, "neptune.desktop")

        if os.path.exists(desktop_global):
            if not os.path.exists(neptune.AUTOSTART_DIR):
                os.mkdir(neptune.AUTOSTART_DIR)
            if neptune.tools.file_exists(desktop_autostart) \
                    in ("file", "broken"):
                os.remove(desktop_autostart)
            if enabled:
                os.symlink(desktop_global, desktop_autostart)
