# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest

from django.contrib.auth import get_user_model, login as django_login
from django.core.urlresolvers import reverse
from django.utils.datastructures import MultiValueDictKeyError

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
    """
    Test whether valid logins succeed and invalid logins fail.
    """
    url = reverse('login')
    data = {'access_level': username, 'password': password}
    response = client.post(url, data=data)
    if success is True:
        msg = 'Login %s / %s failed' % (username, password)
        assert response.status_code == 302, msg
    else:
        msg = 'Login %s / %s shouldn\'t have been valid' % (username, password)
        assert response.status_code == 200, msg


@pytest.mark.parametrize('url, method', [
    # Add views
    ('/groups/add/', 'get'),
    ('/devices/add/', 'get'),
    ('/directories/add/', 'get'),
    ('/regids/add/', 'get'),
    ('/packages/add/', 'get'),
    ('/products/add/', 'get'),
    ('/policies/add/', 'get'),
    ('/enforcements/add/', 'get'),
    # Save views
    ('/groups/save/', 'post'),
    ('/devices/save/', 'post'),
    ('/directories/save/', 'post'),
    ('/files/save/', 'post'),
    ('/regids/save/', 'post'),
    ('/tags/save/', 'post'),
    ('/packages/save/', 'post'),
    ('/products/save/', 'post'),
    ('/policies/save/', 'post'),
    ('/enforcements/save/', 'post'),
    # Delete views
    ('/groups/1/delete/', 'post'),
    ('/devices/1/delete/', 'post'),
    ('/directories/1/delete/', 'post'),
    ('/files/1/delete/', 'post'),
    ('/file_hashes/1/delete/', 'get'),
    ('/regids/1/delete/', 'post'),
    ('/tags/1/delete/', 'post'),
    ('/packages/1/delete/', 'post'),
    ('/products/1/delete/', 'post'),
    ('/policies/1/delete/', 'post'),
    ('/enforcements/1/delete/', 'post'),
    # Check views
    ('/groups/check/', 'post'),
    ('/packages/check/', 'post'),
    ('/products/check/', 'post'),
    ('/policies/check/', 'post'),
    ('/enforcements/check/', 'post'),
    # Other views
    ('/versions/1/toggle/', 'get'),
])
def test_permission_enforced(client, strongtnc_users, url, method):
    do_request = getattr(client, method)

    # Test as admin
    client.login(username='admin-user', password='admin')
    try:
        response = do_request(url)
    except MultiValueDictKeyError:
        # If a MultiValueDictKeyError occurs, this shows that the user did
        # not receive a "403 Forbidden" message. As we don't care about a
        # successful request, an exception is OK for us.
        pass
    else:
        assert response.status_code != 403, 'admin-user should have access to %s' % url

    # Test as readonly
    client.login(username='readonly-user', password='readonly')
    try:
        response = do_request(url)
    except MultiValueDictKeyError:
        pytest.fail('readonly-user should not have access to %s' % url)
    else:
        print('Status code: %d' % response.status_code)
        assert response.status_code == 403, 'readonly-user should not have access to %s' % url
