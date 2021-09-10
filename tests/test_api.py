# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json
import random
import string

from django.contrib.auth.models import User
from django.urls import reverse
from django.db.utils import OperationalError
from django.utils import timezone

import pytest
from model_bakery import baker
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework import status

from .test_swid import swidtag  # NOQA
from apps.authentication.permissions import GlobalPermission
from apps.swid import utils
from apps.swid.api_views import SwidMeasurementView
from apps.swid.models import Tag
from apps.core.models import Session


@pytest.fixture
def api_client(transactional_db):
    """
    Return an authenticated API client.
    """
    user = User.objects.create_user(username='api-test', password='api-test',
                                         email="api-test@example.com")
    user.is_staff = True
    user.save()
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def api_factory():
    """
    Return an APIRequestFactory instance.
    """
    factory = APIRequestFactory()
    return factory


@pytest.fixture
def session(transactional_db):
    """
    Generate a session object with pk=1 and no associated tags.
    """
    time = timezone.now()
    session = baker.make(Session, id=1, time=time, identity__data="tester")
    session.tag_set.clear()
    return session


@pytest.mark.django_db
class TestApiAuth(object):

    def _do_request(self, user):
        client = APIClient()
        if user:
            client.force_authenticate(user=user)
        return client.get('/api/')

    def test_anon(self):
        response = self._do_request(user=None)
        # TODO: Change the following return code to HTTP 401 if
        # https://github.com/tomchristie/django-rest-framework/pull/1611 gets merged.
        #assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_root(self):
        user = User.objects.create_superuser(username='root', password='root', email='a@b.com')
        response = self._do_request(user)
        assert response.status_code == status.HTTP_200_OK

    def test_normal_user(self):
        user = User.objects.create_user(username='user', password='1234', email='a@b.com')
        response = self._do_request(user)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_user(self):
        user = User.objects.create_user(username='staff', password='1234', email='a@b.com')
        user.is_staff = True
        user.save()
        response = self._do_request(user)
        assert response.status_code == status.HTTP_200_OK

    def test_write_access_user(self):
        user = User.objects.create_user(username='admin', password='1234', email='a@b.com')
        perm, _ = GlobalPermission.objects.get_or_create(codename='write_access')
        user.user_permissions.add(perm)
        response = self._do_request(user)
        assert response.status_code == status.HTTP_200_OK


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
    validate(r1, status.HTTP_400_BAD_REQUEST, 'No %s submitted' % list_name)

    # Invalid data param
    data = {'data': 'foo'}
    r1 = json_request(data)
    validate(r1, status.HTTP_400_BAD_REQUEST, 'The submitted "data" parameter does not contain a list')


@pytest.mark.parametrize('filename', [
    'strongswan.short.swidtag',
])
def test_swid_measurement_diff(api_client, session, swidtag, filename):
    software_ids = [
        'strongswan.org__debian_7.4-x86_64-cowsay-3.03+dfsg1-4',
        'strongswan.org__debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3'
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
    software_ids = ['strongswan.org__debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3']
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

        sw_id = "strongswan.org__debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3"
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
            software_id="strongswan.org__debian_7.4-x86_64-strongswan-4.5.2-1.5+deb7u3")

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

    tags = baker.make(Tag, _quantity=5)

    # Unfiltered list
    r = api_client.get(reverse('tag-list'))
    data = json.loads(r.content)
    assert len(data) == 5
    assert len(data[0].keys()) == 10

    # Filter some fields
    r = api_client.get(reverse('tag-list'), data={'fields': 'package_name,id,uri'})
    data = json.loads(r.content)
    assert len(data) == 5
    assert len(data[0].keys()) == 3
    assert sorted(data[0].keys()) == ['id', 'packageName', 'uri']

    # Some invalid fields
    r = api_client.get(reverse('tag-list'), data={'fields': 'id,spam'})
    data = json.loads(r.content)
    assert len(data) == 5
    assert len(data[0].keys()) == 1
    assert list(data[0].keys()) == ['id']

    # Filtered detail page
    r = api_client.get(reverse('tag-detail', args=[tags[0].pk]), data={'fields': 'package_name'})
    data = json.loads(r.content)
    assert len(data.keys()) == 1
    assert list(data.keys()) == ['packageName']

    # Only invalid fields
    r = api_client.get(reverse('tag-detail', args=[tags[0].pk]), data={'fields': 'spam'})
    data = json.loads(r.content)
    assert len(data.keys()) == 0


@pytest.mark.django_db
def test_large_measurement(api_factory):
    """
    Test API calls with more than 999 Software-IDs.
    """
    def make_random_string():
        lst = [random.choice(string.ascii_letters + string.digits) for n in range(15)]
        return ''.join(lst)
    software_ids = [make_random_string() for _ in range(1000)]

    data = {'data': software_ids}
    request = api_factory.post(reverse('session-swid-measurement', args=[1]), data, format='json')

    user = baker.make(User, is_staff=True)
    force_authenticate(request, user=user)

    try:
        SwidMeasurementView.as_view()(request, 1)
    except OperationalError:
        pytest.fail('SWID measurement view should be able to deal with >999 Software-IDs.')
