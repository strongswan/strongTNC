# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone

import pytest
from model_mommy import mommy
from rest_framework.test import APIClient
from rest_framework import status

from .test_swid import swidtag  # NOQA
from apps.swid import utils
from apps.swid.models import Tag
from apps.core.models import Session


@pytest.fixture
def api_client(transactional_db):
    """
    Return an authenticated API client.
    """
    user = User.objects.create_superuser(username='api-test', password='api-test',
                                         email="api-test@example.com")
    user.is_staff = True
    user.save()
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def session(transactional_db):
    """
    Generate a session object with pk=1 and no associated tags.
    """
    time = timezone.now()
    session = mommy.make(Session, id=1, time=time)
    session.tag_set.clear()
    return session


@pytest.mark.parametrize(['url', 'list_name'], [
    (reverse('session-swid-measurement', args=[1]), 'software IDs'),
    (reverse('swid-add-tags'), 'SWID tags'),
])
def test_data_param_validation(api_client, session, url, list_name):

    def validate(response, status_code, message):
        assert response.status_code == status_code
        assert response.data['detail'] == message

    def json_request(data, encode=True):
        if encode:
            return api_client.post(url, data, format='json')
        return api_client.post(url, data, content_type='application/json')

    def form_request(data, encode=True):
        if encode:
            return api_client.post(url, data, format='multipart')
        return api_client.post(url, data, content_type='application/x-www-form-urlencoded')

    # No data
    r1 = json_request('[]', encode=False)
    r2 = form_request('', encode=False)
    # Uncomment the following line if
    # https://github.com/tomchristie/django-rest-framework/pull/1608 gets merged
    validate(r1, status.HTTP_400_BAD_REQUEST, 'Missing "data" parameter')
    validate(r2, status.HTTP_400_BAD_REQUEST, 'No %s submitted' % list_name)

    # Empty data param
    data = {'data': []}
    r1 = json_request(data)
    r2 = form_request(data)
    validate(r1, status.HTTP_400_BAD_REQUEST, 'No %s submitted' % list_name)
    validate(r2, status.HTTP_400_BAD_REQUEST, 'No %s submitted' % list_name)

    # Invalid data param
    data = {'data': 'foo'}
    r1 = json_request(data)
    validate(r1, status.HTTP_400_BAD_REQUEST, 'The submitted "data" parameter does not contain a list')


@pytest.mark.parametrize('filename', [
    'strongswan.short.swidtag',
])
def test_swid_measurement_diff(api_client, session, swidtag, filename):
    software_ids = [
        'regid.2004-03.org.strongswan_debian_7.4-x86_64-cowsay-3.03+dfsg1-4',
        'regid.2004-03.org.strongswan_debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3'
    ]
    data = {'data': software_ids}

    # make call to get diff
    response = api_client.post(reverse('session-swid-measurement', args=[session.id]), data, format='json')
    assert response.status_code == status.HTTP_412_PRECONDITION_FAILED
    assert len(response.data) == 1
    assert software_ids[1] not in response.data
    assert software_ids[0] in response.data
    assert session.tag_set.count() == 0

    # insert missing tag into db
    with open('tests/test_tags/cowsay.short.swidtag') as file:
        utils.process_swid_tag(file.read())

    # make call again
    response = api_client.post(reverse('session-swid-measurement', args=[session.id]), data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
    assert session.tag_set.count() == 2


@pytest.mark.django_db
@pytest.mark.parametrize('filename', [
    'strongswan.short.swidtag',
])
def test_diff_on_invalid_session(api_client, swidtag, filename):
    software_ids = ['regid.2004-03.org.strongswan_debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3']
    data = {'data': software_ids}

    assert Session.objects.filter(pk=1).count() == 0

    # make call to get diff
    response = api_client.post(reverse('session-swid-measurement', args=[1]), data, format='json')
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_add_single_tag(api_client):
    with open('tests/test_tags/strongswan.short.swidtag') as f:
        xml = f.read()
        data = {'data': [xml]}
        response = api_client.post(reverse('swid-add-tags'), data, format='json')
        assert response.status_code == status.HTTP_200_OK

        sw_id = "regid.2004-03.org.strongswan_debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3"
        assert Tag.objects.filter(software_id=sw_id).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('filename', [
    'strongswan.full.swidtag',
])
def test_add_existing_tag(api_client, swidtag, filename):
    assert swidtag.files.count() == 7

    with open('tests/test_tags/strongswan.full.swidtag.singleentity') as f:
        xml = f.read()
        data = {'data': [xml]}
        response = api_client.post(reverse('swid-add-tags'), data, format='json')
        assert response.status_code == status.HTTP_200_OK
        tag = Tag.objects.get(
            software_id="regid.2004-03.org.strongswan_debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3")

        assert tag.files.count() == 7
        assert tag.entityrole_set.count() == 2


@pytest.mark.parametrize('filename', [
    'strongswan.full.swidtag.notagcreator',
    'strongswan.full.swidtag.nouniqueid'
])
def test_invalid_tag(api_client, filename):
    with open('tests/test_tags/invalid_tags/%s' % filename) as f:
        xml = f.read()
        response = api_client.post(reverse('swid-add-tags'), [xml], format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_invalid_xml(api_client):
    response = api_client.post(reverse('swid-add-tags'), ["<?xml "], format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_limit_fields(api_client):
    # TODO convert to class

    tags = mommy.make(Tag, _quantity=5)

    # Unfiltered list
    r = api_client.get(reverse('tag-list'))
    data = json.loads(r.content)
    assert len(data) == 5
    assert len(data[0].keys()) == 7

    # Filter some fields
    r = api_client.get(reverse('tag-list'), data={'fields': 'packageName,id,uri'})
    data = json.loads(r.content)
    assert len(data) == 5
    assert len(data[0].keys()) == 3
    assert sorted(data[0].keys()) == ['id', 'packageName', 'uri']

    # Some invalid fields
    r = api_client.get(reverse('tag-list'), data={'fields': 'id,spam'})
    data = json.loads(r.content)
    assert len(data) == 5
    assert len(data[0].keys()) == 1
    assert data[0].keys() == ['id']

    # Filtered detail page
    r = api_client.get(reverse('tag-detail', args=[tags[0].pk]), data={'fields': 'packageName'})
    data = json.loads(r.content)
    assert len(data.keys()) == 1
    assert data.keys() == ['packageName']

    # Only invalid fields
    r = api_client.get(reverse('tag-detail', args=[tags[0].pk]), data={'fields': 'spam'})
    data = json.loads(r.content)
    assert len(data.keys()) == 0
