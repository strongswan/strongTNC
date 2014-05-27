# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import urllib
import json
import calendar
from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.dateformat import format
from django.utils.timezone import localtime

import pytest
from model_mommy import mommy

from apps.core.models import Session
from apps.filesystem.models import File, Directory
from apps.swid.models import Tag
from apps.devices.models import Device


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
    url = '/dajaxice/%s/' % endpoint
    data = {'argv': json.dumps(payload)}

    # check if test user exists, in case a test calls this function twice
    if not User.objects.filter(username='tester').count():
        User.objects.create_user(username='tester', password='tester')
    client.login(username='tester', password='tester')

    response = client.post(url, data=urllib.urlencode(data),
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
    mommy.make(Session, id=1, time=now - timedelta(days=1), device__id=1)
    mommy.make(Session, id=2, time=now + timedelta(days=1), device__id=1)
    mommy.make(Session, id=3, time=now + timedelta(days=3), device__id=1)
    mommy.make(Session, id=4, time=now - timedelta(days=3), device__id=1)


@pytest.fixture
def get_sessions(client, sessions_test_data):
    def _query(device_id, date_from, date_to):
        payload = {'device_id': device_id, 'date_from': date_from, 'date_to': date_to}
        response_data = ajax_request(client, 'apps.devices.sessions_for_device', payload)
        return response_data['sessions']
    return _query


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
    results = get_completions(search_term, 'apps.filesystem.files_autocomplete', 'file')
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
    results = get_completions(search_term, 'apps.filesystem.directories_autocomplete', 'directory')
    assert sorted(results) == sorted(expected)


### Session Tests ###

@pytest.mark.parametrize('from_diff_to_now, to_diff_to_now, expected', [
    (-2, +2, 2),
    (-3, +3, 4)
])
def test_sessions(get_sessions, from_diff_to_now, to_diff_to_now, expected):
    now = timezone.now()
    date_from = calendar.timegm((now + timedelta(days=from_diff_to_now)).utctimetuple())
    date_to = calendar.timegm((now + timedelta(days=to_diff_to_now)).utctimetuple())
    results = get_sessions(1, date_from, date_to)
    assert len(results) == expected, '%i instead of %i sessions found in the given time range' % \
            (len(results), expected)


def test_tags_for_session(db, client):
    """
    Test whether the ``tags_for_session`` ajax endpoint works properly.
    """
    # Prepare 4 sessions and related tags
    now = localtime(timezone.now())
    for i in range(1, 5):
        time = now + timedelta(days=i)
        session = mommy.make(Session, pk=i, time=time, device__id=1)
        tag = mommy.make(Tag, package_name='name%d' % i)
        tag.sessions.add(session)

    # The second session has two tags
    tag = mommy.make(Tag, package_name='name5')
    tag.sessions.add(2)

    # Test first session
    payload = {'session_id': 1}
    data = ajax_request(client, 'apps.swid.tags_for_session', payload)
    assert data['swid-tag-count'] == 1
    assert len(data['swid-tags']) == 1
    assert data['swid-tags'][0]['name'] == 'name1'
    assert data['swid-tags'][0]['installed'] == (now + timedelta(days=1)).strftime('%b %d %H:%M:%S %Y')

    # Test second session
    payload = {'session_id': 2}
    data = ajax_request(client, 'apps.swid.tags_for_session', payload)
    assert data['swid-tag-count'] == 3
    assert len(data['swid-tags']) == 3
    names = sorted([t['name'] for t in data['swid-tags']])
    assert names == sorted(['name1', 'name2', 'name5'])
    dates = sorted([t['installed'] for t in data['swid-tags']])
    date1 = (now + timedelta(days=1)).strftime('%b %d %H:%M:%S %Y')
    date2 = (now + timedelta(days=2)).strftime('%b %d %H:%M:%S %Y')
    assert dates == [date1, date2, date2]

    # Test all sessions
    payload = {'session_id': 4}
    data = ajax_request(client, 'apps.swid.tags_for_session', payload)
    assert data['swid-tag-count'] == 5
    assert len(data['swid-tags']) == 5


def test_swid_log(transactional_db, client):
    now = timezone.now()
    s1 = mommy.make(Session, id=1, identity__data="tester", time=now - timedelta(days=3), device__id=1)
    s2 = mommy.make(Session, id=2, identity__data="tester", time=now - timedelta(days=1), device__id=1)
    s3 = mommy.make(Session, id=3, identity__data="tester", time=now + timedelta(days=1), device__id=1)
    mommy.make(Session, id=7, identity__data="tester", time=now + timedelta(days=2), device__id=1)
    s4 = mommy.make(Session, id=4, identity__data="tester", time=now + timedelta(days=3), device__id=1)
    mommy.make(Session, id=5, identity__data="tester", time=now - timedelta(days=4), device__id=1)
    mommy.make(Session, id=6, identity__data="tester", time=now + timedelta(days=4), device__id=1)

    tag1 = mommy.make(Tag, id=1)
    tag2 = mommy.make(Tag, id=2)
    tag3 = mommy.make(Tag, id=3)
    tag4 = mommy.make(Tag, id=4)
    tag5 = mommy.make(Tag, id=5)
    tag6 = mommy.make(Tag, id=6)
    tag7 = mommy.make(Tag, id=7)

    # intital set: tag 1-4
    s1.tag_set.add(tag1, tag2, tag3, tag4)
    # s2, added: tag5;
    s2.tag_set.add(tag1, tag2, tag3, tag4, tag5)
    # s3, removed: tag1;
    s3.tag_set.add(tag2, tag3, tag4, tag5)
    # s4 added: tag6, tag7; removed: tag2;
    s4.tag_set.add(tag3, tag4, tag5, tag6, tag7)

    from_timestamp = format(now - timedelta(days=3), u'U')
    to_timestamp = format(now + timedelta(days=4), u'U')

    payload = {
        'device_id': 1,
        'from_timestamp': int(from_timestamp),
        'to_timestamp': int(to_timestamp),
    }
    data = ajax_request(client, 'apps.swid.get_tag_log', payload)

    # there shoulb be three results, bc. 4 session in the range have tags
    assert len(data) == 3
    # the results shoulb be in chronological order
    assert data[0]['session_id'] == 4
    assert data[1]['session_id'] == 3
    assert data[2]['session_id'] == 2
    # checking if removed and added are as expected
    assert data[2]['added_tags'][0]['tag_id'] == 5
    assert data[1]['removed_tags'][0]['tag_id'] == 1
    assert data[0]['removed_tags'][0]['tag_id'] == 2

