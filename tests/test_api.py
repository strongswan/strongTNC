# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest

from rest_framework.test import APIClient
from django.contrib.auth.models import User

from .test_swid import swidtag


@pytest.fixture
def api_client(transactional_db):
    user = User.objects.create_superuser(username='api-test', password='api-test',
                                         email="api-test@example.com")
    user.is_staff = True
    user.save()
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
@pytest.mark.parametrize('filename', [
    'strongswan.short.swidtag'])
def test_swid_measurement_diff(api_client, swidtag, filename):
    software_ids = [
        'regid.2004-03.org.strongswan_cowsay',
        'regid.2004-03.org.strongswan_debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3'
    ]

    response = api_client.post('/api/sessions/2/swid_measurement/', software_ids, format='json')
    assert len(response.data) == 1
    assert software_ids[1] not in response