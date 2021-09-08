# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest

from django.contrib.auth import get_user_model

from apps.authentication.permissions import GlobalPermission


@pytest.fixture
def write_access_perm(transactional_db):
    """
    Provide the ``write_access`` permission.
    """
    perm = GlobalPermission.objects.create(codename='write_access',
            name='Has write access to data.')
    return perm


@pytest.fixture
def strongtnc_users(transactional_db, write_access_perm):
    """
    Provide two users called ``admin-user`` and ``readonly-user`` with correct
    permissions.
    """
    User = get_user_model()
    admin_user = User.objects.create(username='admin-user')
    admin_user.set_password('admin')
    admin_user.user_permissions.add(write_access_perm)
    admin_user.save()
    readonly_user = User.objects.create(username='readonly-user')
    readonly_user.set_password('readonly')
    readonly_user.save()


@pytest.fixture
def test_user(transactional_db):
    """
    Provide a user ``test`` with password ``test``.
    """
    user = get_user_model().objects.create(username='test')
    user.set_password('test')
    user.save()
