# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest
from model_mommy import mommy

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone

from rest_framework.test import APIClient

from .test_swid import swidtag
from apps.swid import utils
from apps.swid.models import Tag
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
    response = api_client.post(reverse('session-swid-measurement', args=[session.id]), software_ids,
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
    response = api_client.post(reverse('session-swid-measurement', args=[session.id]), software_ids,
                               format='json')
    assert response.status_code == 200
    assert len(response.data) == 0
    assert session.tag_set.count() == 2


@pytest.mark.django_db
@pytest.mark.parametrize('filename', [
    'strongswan.short.swidtag',
])
def test_diff_on_invalid_session(api_client, swidtag, filename):
    software_ids = [
        'regid.2004-03.org.strongswan_debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3'
    ]

    assert Session.objects.filter(pk=1).count() == 0

    # make call to get diff
    response = api_client.post(reverse('session-swid-measurement', args=[1]), software_ids,
                               format='json')
    assert response.status_code == 404


@pytest.mark.django_db
def test_add_single_tag(api_client):
    with open('tests/test_tags/strongswan.short.swidtag') as f:
        xml = f.read()
        response = api_client.post(reverse('swid-add-tags'), [xml], format='json')
        assert response.status_code == 200

        sw_id = "regid.2004-03.org.strongswan_debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3"
        assert Tag.objects.filter(software_id=sw_id).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('filename', [
    'strongswan.full.swidtag',
])
def test_add_existing_tag(api_client, swidtag, filename):
    assert len(swidtag.files.all()) == 7

    with open('tests/test_tags/strongswan.full.swidtag.singleentity') as f:
        xml = f.read()
        response = api_client.post(reverse('swid-add-tags'), [xml], format='json')
        assert response.status_code == 200
        tag = Tag.objects.get(
            software_id="regid.2004-03.org.strongswan_debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3")

        assert tag.files.count() == 5
        assert len(tag.entityrole_set.all()) == 1
        assert len(tag.files.all()) == 5


@pytest.mark.parametrize('filename', [
    'strongswan.full.swidtag.notagcreator',
    'strongswan.full.swidtag.nouniqueid'
])
def test_invalid_tag(api_client, filename):
    with open('tests/test_tags/invalid_tags/%s' % filename) as f:
        xml = f.read()
        response = api_client.post(reverse('swid-add-tags'), [xml], format='json')
        assert response.status_code == 400  # Bad request


def test_invalid_xml(api_client):
    response = api_client.post(reverse('swid-add-tags'), ["<?xml "], format='json')
    assert response.status_code == 400  # Bad request