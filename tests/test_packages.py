# -*- coding: utf-8 -*-
"""
Tests for `packages` app.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

from django.urls import reverse
from django.utils import timezone

import pytest
from model_bakery import baker

from apps.packages.models import Version, Package
from apps.devices.models import Product

from .fixtures import *  # NOQA: Star import is OK here because it's just a test


@pytest.fixture
def package_testdata(transactional_db):
    package = baker.make(Package, pk=1)
    product = baker.make(Product, pk=1)
    time = timezone.now()
    baker.make(Version, pk=1, product=product, package=package, release='1.0', security=True, blacklist=True,
               time=time)
    return package

def test_save_version_validation(strongtnc_users, client, package_testdata):
    # Log in
    client.login(username='admin-user', password='admin')
    url = reverse('packages:add_package_version', args='1')

    data = {}

    def do_request(reason):
        resp = client.post(url, json=data)
        assert resp.status_code == 400, reason

    # Missing data
    do_request('Missing data')

    # Invalid version
    for value in [None, '']:
        data['version'] = value
        do_request('Invalid version (%s)' % value)
    data['version'] = '1.0'
    data['blacklist'] = 'on'
    data['security'] = 'on'


    # Invalid product
    data['product'] = 999
    do_request('Invalid product')

    data['product'] = 1

    # Valid request
    response = client.post(url, data)
    assert response.status_code == 302
