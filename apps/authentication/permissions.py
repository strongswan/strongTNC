# -*- coding: utf-8 -*-
"""
This module contains a proxy model and a custom manager to handle permissions
that are not tied to any model. The implementation is strongly based on the
StackOverflow solution at http://stackoverflow.com/a/13952198/284318.

Usage example::

    from apps.authentication.permissions import GlobalPermission
    gp = GlobalPermission.objects.create(codename='can_do_it', name='Can do it')

Now you have a global permission called ``can_do_it`` that is not tied to any
specific model.

"""
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from rest_framework import permissions


class GlobalPermissionManager(models.Manager):
    """
    This manager filters queries and returns only items where the content
    type is "Global Permission".
    """
    def get_query_set(self):
        return super(GlobalPermissionManager, self).\
            get_query_set().filter(content_type__model='global_permission')


class GlobalPermission(Permission):
    """
    A global permission, not attached to a specific model.
    """

    objects = GlobalPermissionManager()

    class Meta(object):
        proxy = True
        verbose_name = 'global_permission'

    def save(self, *args, **kwargs):
        # Ensure that a content type called 'global_permission' exists
        ct, created = ContentType.objects.get_or_create(
            model=self._meta.verbose_name, app_label='auth'
        )
        # Assign the 'global_permission' content type to this permission
        self.content_type = ct
        super(GlobalPermission, self).save(*args, **kwargs)


class IsStaffOrHasWritePerm(permissions.BasePermission):
    """
    Django Rest Framework permission class.

    It allows access to the API if it has the `is_staff` flag set, or
    if it has the global `auth.write_access` permission assigned. (See
    `apps/auth/management/commands/setpassword.py` to see an example on
    how to assign that permission programmatically.)

    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        if request.user.has_perm('auth.write_access'):
            return True
        return False
