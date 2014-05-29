# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.conf import settings
from django.utils.timezone import localtime


def local_dtstring(timestamp):
    """
    Return a formatted (strongTNC standard format) date string.
    """
    return localtime(timestamp).strftime(settings.DEFAULT_DATETIME_FORMAT_STRING)
