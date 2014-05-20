# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models

from apps.core.fields import EpochField


class Package(models.Model):
    """
    A Package.
    """
    name = models.CharField(max_length=255, db_index=True)

    class Meta:
        db_table = 'packages'

    def __unicode__(self):
        return self.name

    def list_repr(self):
        """
        String representation in lists
        """
        return self.name


class Version(models.Model):
    """
    Version number string of a package.
    """
    package = models.ForeignKey(Package, db_column='package', related_name='versions')
    product = models.ForeignKey('devices.Product', db_column='product', related_name='versions')
    release = models.CharField(max_length=255, db_index=True)
    security = models.BooleanField(default=0)
    blacklist = models.IntegerField(null=True, blank=True)
    time = EpochField()

    class Meta:
        db_table = 'versions'
        index_together = [('package', 'product')]

    def __unicode__(self):
        return self.release

    def list_repr(self):
        """
        String representation in lists
        """
        return self.release
