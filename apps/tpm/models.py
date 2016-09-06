# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models

from apps.core.fields import HashField
from apps.devices.models import Device
from apps.filesystem.models import Algorithm


class Component(models.Model):
    """
    A component.
    """
    vendor_id = models.IntegerField()
    name = models.IntegerField()
    qualifier = models.IntegerField(default=0)
    label = models.CharField(max_length=255)

    class Meta:
        db_table = 'components'

    def __unicode__(self):
        return '%s' % (self.label)

    def list_repr(self):
        """
        String representation in lists
        """
        return '%s' % (self.label)


class ComponentHash(models.Model):
    """
    A component hash.
    """
    component = models.ForeignKey(Component, db_column='component')
    device = models.ForeignKey('devices.Device', db_column='key')
    seq_no = models.IntegerField()
    pcr = models.IntegerField()
    algorithm = models.ForeignKey('filesystem.Algorithm', db_column='algo')
    hash = HashField(db_column='hash')

    class Meta:
        db_table = 'component_hashes'
        verbose_name_plural = 'component hashes'
        ordering = ('device', 'component', 'seq_no',)

    def __unicode__(self):
        return '%s (%s)' % (self.hash, self.algorithm)

    def list_repr(self):
        """
        String representation in lists
        """
        return '%s (%s)' % (self.hash, self.algorithm)
