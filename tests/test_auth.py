# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import urllib
import pytest
import json

from django.core.urlresolvers import reverse
from django.utils.datastructures import MultiValueDictKeyError

from .fixtures import *  # NOQA: Star import is OK here because it's just a test


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
    url = reverse('auth:login')
    data = {'access_level': username, 'password': password}
    response = client.post(url, data=data)
    if success is True:
        msg = 'Login %s / %s failed' % (username, password)
        assert response.status_code == 302, msg
    else:
        msg = 'Login %s / %s shouldn\'t have been valid' % (username, password)
        assert response.status_code == 200, msg


@pytest.mark.parametrize('url', [
    # SWID views
    '/regids/',
    '/regids/1/',
    '/swid-tags/',
    '/swid-tags/1/',
])
def test_login_required(client, strongtnc_users, url):
    # Test as anonymous
    response = client.get(url)
    assert response.status_code == 302, 'Unauthenticated user should not have access to %s' % url

    # Test as readonly
    client.login(username='readonly-user', password='readonly')
    response = client.get(url)
    assert response.status_code != 302, 'Readonly user should have access to %s' % url

    # Test as admin
    client.login(username='admin-user', password='admin')
    response = client.get(url)
    assert response.status_code != 302, 'Admin user should have access to %s' % url


@pytest.mark.parametrize('url, method', [
    # Add views
    ('/groups/add/', 'get'),
    ('/devices/add/', 'get'),
    ('/files/add/', 'get'),
    ('/directories/add/', 'get'),
    ('/packages/add/', 'get'),
    ('/products/add/', 'get'),
    ('/policies/add/', 'get'),
    ('/enforcements/add/', 'get'),
    # Save views
    ('/groups/save/', 'post'),
    ('/devices/save/', 'post'),
    ('/directories/save/', 'post'),
    ('/files/save/', 'post'),
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
    ('/packages/1/delete/', 'post'),
    ('/products/1/delete/', 'post'),
    ('/policies/1/delete/', 'post'),
    ('/enforcements/1/delete/', 'post'),
    # Check views
    ('/groups/check/', 'post'),
    ('/devices/check/', 'post'),
    ('/packages/check/', 'post'),
    ('/products/check/', 'post'),
    ('/policies/check/', 'post'),
    ('/enforcements/check/', 'post'),
    ('/directories/check/', 'post'),
    # Other views
    ('/versions/1/toggle/', 'get'),
])
def test_write_permission_enforced(client, strongtnc_users, url, method):
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


@pytest.mark.parametrize('endpoint, payload', [
    ('apps.filesystem.files_autocomplete', {'search_term': 'bash'}),
    ('apps.filesystem.directories_autocomplete', {'search_term': 'bash'}),
    ('apps.swid.get_tag_stats', {'session_id': 1}),
    ('apps.swid.get_tag_log_stats', {'device_id': 1, 'date_from': '', 'date_to': ''}),
    ('apps.devices.sessions_for_device', {'device_id': 1, 'date_from': '', 'date_to': ''}),
    ('apps.front.paging', {'template': '', 'list_producer': '', 'stat_producer': '', 'var_name': '',
        'url_name': '', 'current_page': '', 'page_size': '', 'filter_query': '', 'pager_id': ''}),
])
def test_ajax_login_required(client, endpoint, payload):
    url = '/dajaxice/%s/' % endpoint
    data = {'argv': json.dumps(payload)}

    response = client.post(url, data=urllib.urlencode(data),
                           content_type='application/x-www-form-urlencoded',
                           HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    assert response.status_code == 200
    assert response.content == 'DAJAXICE_EXCEPTION'
