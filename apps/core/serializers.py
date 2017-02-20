# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from apps.api.mixins import DynamicFieldsMixin
from . import models


class IdentitySerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Identity
        fields = ('id', 'uri', 'type', 'data')


class SessionSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    # PrimaryKey fields are only needed until endpoints exists
    device = serializers.PrimaryKeyRelatedField()

    class Meta(object):
        model = models.Session
        fields = ('id', 'uri', 'time', 'identity', 'connection_id', 'device', 'recommendation')
