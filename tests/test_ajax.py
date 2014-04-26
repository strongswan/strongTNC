# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import urllib
import json

import pytest

from tncapp import models


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
def get_completions(client, files_and_directories_test_data):
    """
    Fixture that provides a parametrized function that queries the
    autocompletion AJAX endpoint. That function, when called with a search
    term, returns a list of matching file paths.
    """
    def _query(term, url, key):
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