# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models

from apps.core.fields import HashField


class Component(models.Model):
    """
    A component.
    """
    vendor_id = models.IntegerField()
    name = models.IntegerField()
    qualifier = models.IntegerField(default=0)
    label = models.CharField(max_length=255)

    class Meta(object):
        db_table = 'components'

    def __str__(self):
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
    component = models.ForeignKey(Component, db_column='component',
                        on_delete=models.CASCADE)
    device = models.ForeignKey('devices.Device', db_column='key',
                        on_delete=models.CASCADE)
    seq_no = models.IntegerField()
    pcr = models.IntegerField()
    algorithm = models.ForeignKey('filesystem.Algorithm', db_column='algo',
                        on_delete=models.CASCADE)
    hash = HashField(db_column='hash')

    class Meta(object):
        db_table = 'component_hashes'
        verbose_name_plural = 'component hashes'
        ordering = ('device', 'component', 'seq_no',)

    def __str__(self):
        return '%s (%s)' % (self.hash, self.algorithm)

    def list_repr(self):
        """
        String representation in lists
        """
        return '%s (%s)' % (self.hash, self.algorithm)
