# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from . import models


class IdentitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Identity
        fields = ('id', 'uri', 'type', 'data')


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    # PrimaryKey fields are only needed until endpoints exists
    device = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = models.Session
        fields = ('id', 'uri', 'time', 'identity', 'connection_id', 'device', 'recommendation')
