# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from apps.api.mixins import DynamicFieldsMixin
from apps.devices.serializers import DeviceMiniSerializer

from . import models


class IdentitySerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Identity
        fields = ('id', 'uri', 'type', 'data')


class IdentityMiniSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Identity
        fields = ('uri', 'data')


class SessionSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    device = DeviceMiniSerializer()
    identity = IdentityMiniSerializer()
    time = serializers.DateTimeField()

    class Meta(object):
        model = models.Session
        fields = ('id', 'uri', 'time', 'identity', 'connection_id', 'device', 'recommendation')


class ResultSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    session = SessionSerializer()

    class Meta(object):
        model = models.Result
        fields = ('id', 'uri', 'session', 'policy', 'result', 'recommendation')
