# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import urllib
import json
import calendar
from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

import pytest
from model_bakery import baker

from apps.core.models import Session
from apps.filesystem.models import File, Directory


### Helper functions ###

def ajax_request(client, endpoint, payload):
    """
    Simplify the sending of an AJAX request.

    Args:
        endpoint (str):
            The AJAX endpoint, e.g. ``apps.devices.sessions_for_device``.
        payload (dict):
            The HTTP POST arguments.

    Returns:
        The JSON response data as a dictionary.

    """
    # check if test user exists, in case a test calls this function twice
    if not User.objects.filter(username='tester').count():
        User.objects.create_user(username='tester', password='tester')
    client.login(username='tester', password='tester')

    response = client.post(endpoint, data=urllib.parse.urlencode(payload),
                           content_type='application/x-www-form-urlencoded',
                           HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    return json.loads(response.content)


### Fixtures ###

@pytest.fixture
def files_and_directories_test_data(transactional_db):
    """
    Create Directory and File objects in the test database.
    """
    # Directories
    root_dir = Directory.objects.create(path='/')
    bin_dir = Directory.objects.create(path='/bin')
    usr_dir = Directory.objects.create(path='/usr')
    usr_bin_dir = Directory.objects.create(path='/usr/bin')
    etc_dir = Directory.objects.create(path='/etc')
    Directory.objects.create(path='/system/lib/etc')
    Directory.objects.create(path='/usr/lib')

    # Files
    for name in ['rootfile', 'etcetera']:
        File.objects.create(directory=root_dir, name=name)
    for name in ['bash', 'chmod']:
        File.objects.create(directory=bin_dir, name=name)
    for name in ['user1', 'user2']:
        File.objects.create(directory=usr_dir, name=name)
    for name in ['2to3', 'alsamixer']:
        File.objects.create(directory=usr_bin_dir, name=name)
    File.objects.create(directory=etc_dir, name='hosts')


@pytest.fixture
def sessions_test_data(transactional_db):
    now = timezone.now()
    baker.make(Session, id=1, time=now - timedelta(days=1), device__id=1)
    baker.make(Session, id=2, time=now + timedelta(days=1), device__id=1)
    baker.make(Session, id=3, time=now + timedelta(days=3), device__id=1)
    baker.make(Session, id=4, time=now - timedelta(days=3), device__id=1)


@pytest.fixture
def get_completions(client, files_and_directories_test_data):
    """
    Fixture that provides a parametrized function that queries the
    autocompletion AJAX endpoint. That function, when called with a search
    term, returns a list of matching file paths.
    """
    def _query(term, endpoint, key):
        payload = {'search_term': term}
        response_data = ajax_request(client, endpoint, payload)
        return [r[key] for r in response_data['results']]
    return _query


### Autocompletion Tests ###

@pytest.mark.parametrize('search_term, expected', [
    # Prefix completion
    ('/bin/ba', ['/bin/bash']),
    # Completion in root dir
    ('/roo', ['/rootfile']),
    # Suffix completion
    ('bash', ['/bin/bash']),
    # Completion anywhere in string
    ('user', ['/usr/user1', '/usr/user2']),
    ('/2', ['/usr/bin/2to3', '/usr/user2']),
    # Completion of full directory
    ('/etc', ['/etc/hosts', '/etcetera']),
    ('/etc/', ['/etc/hosts']),
    # Completion of both files and directories containing same string
    ('etc', ['/etcetera', '/etc/hosts']),
    # Complete everything
    ('/', ['/rootfile', '/etcetera',
           '/bin/bash', '/bin/chmod',
           '/usr/user1', '/usr/user2',
           '/usr/bin/2to3', '/usr/bin/alsamixer',
           '/etc/hosts']),
    # No results
    ('/saberthoothtigerdinozord', [])
])
def test_files_autocomplete(get_completions, search_term, expected):
    results = get_completions(search_term, '/files/autocomplete', 'file')
    assert sorted(results) == sorted(expected)


@pytest.mark.parametrize('search_term, expected', [
    # 01
    ('/bin', ['/bin', '/usr/bin']),
    # 02
    ('usr', ['/usr', '/usr/bin', '/usr/lib']),
    # 03
    ('etc', ['/etc', '/system/lib/etc']),
    # 04
    ('tem', ['/system/lib/etc']),
    ('lib', ['/system/lib/etc', '/usr/lib']),
    # 05
    ('/etc', ['/etc', '/system/lib/etc']),
    # 06
    ('/', ['/', '/bin', '/usr', '/usr/bin',
           '/etc', '/system/lib/etc', '/usr/lib']),
    # No results
    ('/saberthoothtigerdinozord', [])
])
def test_directory_autocomplete(get_completions, search_term, expected):
    results = get_completions(search_term, '/directories/autocomplete', 'directory')
    assert sorted(results) == sorted(expected)
