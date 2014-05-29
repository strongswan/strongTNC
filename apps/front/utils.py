# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.conf import settings
from django.utils.timezone import localtime


def local_dtstring(timestamp):
    """
    Return a formatted (strongTNC standard format) date string.
    """
    return localtime(timestamp).strftime(settings.DEFAULT_DATETIME_FORMAT_STRING)


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
