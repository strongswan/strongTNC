# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import binascii
import calendar
from datetime import datetime

from django.db import models

import pytz


class HashField(models.BinaryField):
    """
    Custom field type to display file hashes
    """
    def from_db_value(self, value, expression, connection, context):
        return binascii.hexlify(value)

    def to_python(self, value):
        return binascii.hexlify(value)

    def get_prep_value(self, value):
        return binascii.unhexlify(value)


class EpochField(models.IntegerField):
    """
    Custom field type for unix timestamps.
    """
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        dt = datetime.utcfromtimestamp(value)
        return dt.replace(tzinfo=pytz.utc)  # Make datetime timezone-aware

    def to_python(self, value):
        if isinstance(value, (int, long)):
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
