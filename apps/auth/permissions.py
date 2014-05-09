# -*- coding: utf-8 -*-
"""
This module contains a proxy model and a custom manager to handle permissions
that are not tied to any model. The implementation is strongly based on the
StackOverflow solution at http://stackoverflow.com/a/13952198/284318.

Usage example::

    from apps.auth.permissions import GlobalPermission
    gp = GlobalPermission.objects.create(codename='can_do_it', name='Can do it')

Now you have a global permission called ``can_do_it`` that is not tied to any
specific model.

"""
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class GlobalPermissionManager(models.Manager):
    """
    This manager filters queries and returns only items where the content
    type is "Global Permission".
    """
    def get_query_set(self):
        return super(GlobalPermissionManager, self).\
            get_query_set().filter(content_type__name='global_permission')


class GlobalPermission(Permission):
    """
    A global permission, not attached to a specific model.
    """

    objects = GlobalPermissionManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        # Ensure that a content type called 'global_permission' exists
        ct, created = ContentType.objects.get_or_create(
            name='global_permission', app_label=self._meta.app_label
        )
        # Assign the 'global_permission' content type to this permission
        self.content_type = ct
        super(GlobalPermission, self).save(*args, **kwargs)
