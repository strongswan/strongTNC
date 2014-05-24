# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import binascii
import calendar
from datetime import datetime

from django.db import models

import pytz


class BinaryField(models.Field):
    """
    Custom field type for Binary data
    """
    description = "Raw binary data for SQLite"

    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        super(BinaryField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        """Internal database field type."""
        return 'blob'


class HashField(BinaryField):
    """
    Custom field type to display file hashes
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        return binascii.hexlify(value)

    def get_prep_value(self, value):
        return binascii.unhexlify(value)


class EpochField(models.IntegerField):
    """
    Custom field type for unix timestamps.
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, int):
            dt = datetime.utcfromtimestamp(value)
            return dt.replace(tzinfo=pytz.utc)  # Make datetime timezone-aware
        elif isinstance(value, datetime):
            return value
        elif value is None:
            return None
        else:
            raise ValueError('Invalid type for epoch field: %s' % type(value))

    def get_prep_value(self, value):
        if value:
            return calendar.timegm(value.utctimetuple())
        return None
