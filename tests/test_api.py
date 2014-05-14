# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest
from model_mommy import mommy

from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework.test import APIClient

from .test_swid import swidtag
from apps.swid import utils
from apps.core.models import Session


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
    'strongswan.short.swidtag',
])
def test_swid_measurement_diff(api_client, swidtag, filename):
    software_ids = [
        'regid.2004-03.org.strongswan_debian_7.4-x86_64-cowsay-3.03+dfsg1-4',
        'regid.2004-03.org.strongswan_debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3'
    ]

    time = timezone.now()
    session = mommy.make(Session, id=1, time=time)
    session.tag_set.clear()

    # make call to get diff
    response = api_client.post('/api/sessions/%i/swid_measurement/' % session.id, software_ids,
                               format='json')
    assert response.status_code == 412
    assert len(response.data) == 1
    assert software_ids[1] not in response.data
    assert software_ids[0] in response.data
    assert session.tag_set.count() == 0

    # insert missing tag into db
    with open('tests/test_tags/cowsay.short.swidtag') as file:
        utils.process_swid_tag(file.read())

    # make call again
    response = api_client.post('/api/sessions/%i/swid_measurement/' % session.id, software_ids,
                               format='json')
    assert response.status_code == 200
    assert len(response.data) == 0
    assert session.tag_set.count() == 2

