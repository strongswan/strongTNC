# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from datetime import datetime
from calendar import timegm

from django.conf import settings
from django.utils.timezone import localtime, get_current_timezone


def local_dtstring(datetime):
    """
    Return a formatted (strongTNC standard format) date string.

    Args:
        datetime (datetime.datetime):
            An aware datetime object.

    Returns:
        A string.

    """
    return localtime(datetime).strftime(settings.DEFAULT_DATETIME_FORMAT_STRING)


def timestamp_local_to_utc(timestamp):
    """
    Convert a "local" timestamp to an UTC based one.

    Args:
        timestamp (int):
            A local unix timestamp.

    """
    tz = get_current_timezone()
    dt = datetime.fromtimestamp(timestamp, tz=tz)
    return timegm(dt.timetuple())


def check_not_empty(value):
    """
    Return the value if it is not 'None', None or ''
    Otherwise raise an HttpResponseBadRequest with status code 400
    """
    if value == 'None' or value is None or value == '':
        raise ValueError('Validation failed')
    else:
        return value


def checkbox_boolean(value):
    """
    Convert checkbox form data to boolean
    """
    return True if value == 'on' else False
