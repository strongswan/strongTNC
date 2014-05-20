# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models

from apps.core.fields import HashField


class Component(models.Model):
    vendor_id = models.IntegerField()
    name = models.IntegerField()
    qualifier = models.IntegerField(default=0)
    label = models.CharField(max_length=255)

    class Meta:
        db_table = 'components'


class ComponentHash(models.Model):
    # TODO missing "id" primary key in database
    component = models.ForeignKey(Component)
    device = models.ForeignKey('devices.Device', db_column='key')
    seq_no = models.IntegerField()
    pcr = models.IntegerField()
    algorithm = models.ForeignKey('filesystem.Algorithm', db_column='algo')
    hash = HashField()

    class Meta:
        db_table = 'component_hashes'
        verbose_name_plural = 'component hashes'
