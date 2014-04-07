# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from tncapp.permissions import GlobalPermission


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


@pytest.mark.parametrize('username, password, success', [
    ('admin-user', 'admin', True),
    ('admin-user', 'readonly', False),
    ('readonly-user', 'readonly', True),
    ('readonly-user', 'admin', False),
    ('test', 'test', False),  # Valid credentials but non-authorized username
])
def test_login(client, strongtnc_users, test_user, username, password, success):
    """Test whether valid logins succeed and invalid logins fail."""
    url = reverse('login')
    data = {'access_level': username, 'password': password}
    response = client.post(url, data=data)
    if success is True:
        msg = 'Login %s / %s failed' % (username, password)
        assert response.status_code == 302, msg
    else:
        msg = 'Login %s / %s shouldn\'t have been valid' % (username, password)
        assert response.status_code == 200, msg
