# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import urllib
import json
import calendar
from datetime import timedelta

from django.utils import timezone

import pytest
from model_mommy import mommy

from tncapp import models
from apps.swid import models as new_models


@pytest.fixture
def session_with_tags(transactional_db):
    now = timezone.now()
    device = mommy.make(models.Device)
    tag = mommy.make(new_models.Tag, unique_id='fedora_19-x86_64-strongswan-5.1.2-4.fc19',
                     package_name='strongswan', version='5.1.2-4.fc19')
    tag2 = mommy.make(new_models.Tag, unique_id='fedora_19-x86_64-strongswan2-5.1.2-4.fc19',
                      package_name='strongswan2', version='5.1.2-4.fc19')
    session = mommy.make(models.Session, device=device, time=now)
    tag.sessions.add(session)
    tag2.sessions.add(session)
    return session


@pytest.fixture
def files_and_directories_test_data(transactional_db):
    """
    Create Directory and File objects in the test database.
    """
    # Directories
    root_dir = models.Directory.objects.create(path='/')
    bin_dir = models.Directory.objects.create(path='/bin')
    usr_dir = models.Directory.objects.create(path='/usr')
    usr_bin_dir = models.Directory.objects.create(path='/usr/bin')
    etc_dir = models.Directory.objects.create(path='/etc')
    models.Directory.objects.create(path='/system/lib/etc')
    models.Directory.objects.create(path='/usr/lib')

    # Files
    for name in ['rootfile', 'etcetera']:
        models.File.objects.create(directory=root_dir, name=name)
    for name in ['bash', 'chmod']:
        models.File.objects.create(directory=bin_dir, name=name)
    for name in ['user1', 'user2']:
        models.File.objects.create(directory=usr_dir, name=name)
    for name in ['2to3', 'alsamixer']:
        models.File.objects.create(directory=usr_bin_dir, name=name)
    models.File.objects.create(directory=etc_dir, name='hosts')


@pytest.fixture
def sessions_test_data(transactional_db):
    now = timezone.now()
    mommy.make(models.Session, id=1, time=now - timedelta(days=1), device__id=1)
    mommy.make(models.Session, id=2, time=now + timedelta(days=1), device__id=1)
    mommy.make(models.Session, id=3, time=now + timedelta(days=3), device__id=1)
    mommy.make(models.Session, id=4, time=now - timedelta(days=3), device__id=1)


@pytest.fixture
def get_sessions(client, sessions_test_data):
    def _query(device_id, date_from, date_to):
        url = '/dajaxice/tncapp.sessions_for_device/'
        payload = {'device_id': device_id, 'date_from': date_from, 'date_to': date_to}
        data = {'argv': json.dumps(payload)}
        response = client.post(url, data=urllib.urlencode(data),
                               content_type='application/x-www-form-urlencoded',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response_data = json.loads(response.content)
        return response_data['sessions']

    return _query


@pytest.fixture
def get_completions(client, files_and_directories_test_data):
    """
    Fixture that provides a parametrized function that queries the
    autocompletion AJAX endpoint. That function, when called with a search
    term, returns a list of matching file paths.
    """
    def _query(term, url, key):
        url = '/dajaxice/tncapp.files_autocomplete/'
        payload = {'search_term': term}
        data = {'argv': json.dumps(payload)}
        response = client.post(url, data=urllib.urlencode(data),
                               content_type='application/x-www-form-urlencoded',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response_data = json.loads(response.content)
        results = response_data['results']
        return [r[key] for r in results]

    return _query


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
    results = get_completions(search_term, '/dajaxice/tncapp.files_autocomplete/', 'file')
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
    results = get_completions(search_term, '/dajaxice/tncapp.directories_autocomplete/', 'directory')
    assert sorted(results) == sorted(expected)


@pytest.mark.parametrize('from_diff_to_now, to_diff_to_now, expected', [
    (-2, +2, 2),
    (-3, +3, 4)
])
def test_sessions(get_sessions, from_diff_to_now, to_diff_to_now, expected):
    now = timezone.now()
    date_from = calendar.timegm((now + timedelta(days=from_diff_to_now)).utctimetuple())
    date_to = calendar.timegm((now + timedelta(days=to_diff_to_now)).utctimetuple())
    results = get_sessions(1, date_from, date_to)
    assert len(results) == expected, 'not exactly %i sessions found in the given time range' % expected


def test_session_tags(session_with_tags):
    assert len(session_with_tags.tag_set.all()) == 2