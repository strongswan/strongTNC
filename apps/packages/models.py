# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models
from django.utils import timezone

from apps.core.fields import EpochField


class Package(models.Model):
    """
    A Package.
    """
    name = models.CharField(max_length=255, db_index=True)

    class Meta(object):
        db_table = 'packages'
        ordering = ('name',)

    def __str__(self):
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
    package = models.ForeignKey(Package, db_column='package',
                        on_delete=models.CASCADE, related_name='versions')
    product = models.ForeignKey('devices.Product', db_column='product',
                        on_delete=models.CASCADE, related_name='versions')
    release = models.CharField(max_length=255, db_index=True)
    security = models.BooleanField(default=False)
    blacklist = models.BooleanField(default=False)
    time = EpochField(default=timezone.now())

    class Meta(object):
        db_table = 'versions'
        index_together = [('package', 'product')]
        ordering = ('package', 'release',)

    def __str__(self):
        return self.release

    def list_repr(self):
        """
        String representation in lists
        """
        return '%s %s' % (self.package.name, self.release)
