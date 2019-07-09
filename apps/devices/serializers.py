# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from apps.api.mixins import DynamicFieldsMixin
from . import models


class ProductSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Product
        fields = ('id', 'uri', 'name')


class DeviceSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    product = ProductSerializer()
    created = serializers.DateTimeField()

    class Meta(object):
        model = models.Device
        fields = ('id', 'uri', 'value', 'description', 'product', 'created', 'trusted', 'inactive')


class DeviceMiniSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Device
        fields = ('uri', 'value', 'description')
