# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from apps.api.mixins import DynamicFieldsMixin
from apps.devices.serializers import ProductSerializer
from . import models


class PackageSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Package
        fields = ('id', 'uri', 'name')


class VersionSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    package = PackageSerializer()
    product = ProductSerializer()
    time = serializers.DateTimeField()

    class Meta(object):
        model = models.Version
        fields = ('id', 'uri', 'package', 'product', 'release', 'security', 'blacklist', 'time')
