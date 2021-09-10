# -*- coding: utf-8 -*-
"""
Tests for `policies` app.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

from django.urls import reverse

import pytest
from model_bakery import baker

from apps.policies.models import Policy, Enforcement
from apps.devices.models import Group

from .fixtures import *  # NOQA: Star import is OK here because it's just a test


@pytest.fixture
def policy_testdata(transactional_db):
    p = baker.make(Policy, pk=1)
    g = baker.make(Group, pk=1)
    baker.make(Enforcement, pk=1, policy=p, group=g)


def test_save_enforcement_validation(strongtnc_users, client, policy_testdata):
    # Log in
    client.login(username='admin-user', password='admin')
    url = reverse('policies:enforcement_save')

    data = {}

    invalid_ids = ['', 'new', '-1']
    def do_request(reason):
        response = client.post(url, data=data)
        assert response.status_code == 400, reason

    # Missing data
    do_request('Missing data')

    # Invalid enforcement ID
    for value in invalid_ids:
        data['enforcementId'] = value
        do_request('Invalid enforcementId (%s)' % value)
    data['enforcementId'] = 1

    # Invalid max_age
    for value in invalid_ids:
        data['max_age'] = value
        do_request('Invalid max_age (%s)' % value)
    data['max_age'] = 1

    # Invalid policy
    for value in invalid_ids + [2]:
        data['policy'] = value
        do_request('Invalid policy (%s)' % value)
    data['policy'] = 1

    # Invalid group
    for value in invalid_ids + [2]:
        data['group'] = value
        do_request('Invalid group (%s)' % value)
    data['group'] = 1

    # Invalid fail action
    for value in [-2, len(Policy.action), 'foo']:
        data['fail'] = value
        do_request('Invalid fail action (%s)' % value)
    data['fail'] = 1

    # Invalid noresult action
    for value in [-2, len(Policy.action), 'foo']:
        data['noresult'] = value
        do_request('Invalid noresult action (%s)' % value)
    data['noresult'] = 1

    # Valid request
    response = client.post(url, data)
    assert response.status_code == 302
