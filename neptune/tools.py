#!/usr/bin/env python3
# -*-coding: utf-8-*-

"""Tools"""

from __future__ import (division, absolute_import, unicode_literals,
                        print_function)

# tools: *.py, ../bin/*.py

# pylint: disable=C0302

import six
import chardet
import os


def to_unicode(output):
    """Autodetect unicode"""
    if isinstance(output, six.text_type):
        # already unicode
        return output
    elif output is None or len(output) == 0:
        return ""
    elif isinstance(output, (six.string_types, six.binary_type)):
        detect = chardet.detect(output)
        return output.decode(detect["encoding"])
    else:
        return "{0}".format(output)


def file_exists(name):
    """none: file does not exists
        file: file does exist
        broken: file is a broken sublink
        """

    try:
        os.lstat(name)
    except OSError:
        return "none"

    if os.path.exists(name):
        return "file"
    else:
        return "broken"
