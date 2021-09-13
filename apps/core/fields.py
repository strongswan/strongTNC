# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import binascii
import calendar
from datetime import datetime

from django.db import models

import pytz


class DataField(models.TextField):
    """
    Custom field type to display identity data
    """
    def from_db_value(self, value, expression, connection, *args, **kwargs):
        return value.decode('utf-8')

    def to_python(self, value):
        return value.decode('utf-8')

    def get_prep_value(self, value):
        return bytes(value, 'utf-8')


class HashField(models.BinaryField):
    """
    Custom field type to display file hashes
    """
    def from_db_value(self, value, expression, connection, *args, **kwargs):
        return binascii.hexlify(value).decode('ascii')

    def to_python(self, value):
        return binascii.hexlify(value).decode('ascii')

    def get_prep_value(self, value):
        return binascii.unhexlify(bytes(value, 'ascii'))


class EpochField(models.IntegerField):
    """
    Custom field type for unix timestamps.
    """
    def from_db_value(self, value, expression, connection, *args, **kwargs):
        if value is None:
            return value
        dt = datetime.utcfromtimestamp(value)
        return dt.replace(tzinfo=pytz.utc)  # Make datetime timezone-aware

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
