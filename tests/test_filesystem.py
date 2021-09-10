# -*- coding: utf-8 -*-
"""
Tests for `policies` app.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

from django.urls import reverse

import pytest
from model_bakery import baker

from apps.filesystem.models import File, Directory

from .fixtures import *  # NOQA: Star import is OK here because it's just a test


@pytest.fixture
def file_testdata(transactional_db):
    dir_obj = baker.make(Directory, pk=1)
    baker.make(File, pk=1, name='the_file', directory=dir_obj)


def test_save_file_validation(strongtnc_users, client, file_testdata):
    # Log in
    client.login(username='admin-user', password='admin')
    url = reverse('filesystem:file_save')

    data = {}

    def do_request(reason):
        resp = client.post(url, json=data)
        assert resp.status_code == 400, reason

    # Missing data
    do_request('Missing data')

    # Invalid name
    for value in [None, '']:
        data['name'] = value
        do_request('Invalid name (%s)' % value)
    data['name'] = 'new_flie'

    # Invalid dir
    for value in [None, '', 'new', '-1']:
        data['dir'] = value
        do_request('Invalid dir (%s)' % value)
    data['dir'] = '1'

    # Valid request
    response = client.post(url, data)
    assert response.status_code == 302
