# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from apps.api.mixins import DynamicFieldsMixin
from apps.packages.serializers import VersionSerializer
from apps.devices.serializers import DeviceSerializer
from . import models


class AlgorithmSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Algorithm
        fields = ('id', 'uri', 'name')


class DirectorySerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Directory
        fields = ('id', 'uri', 'path')


class FileSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    directory = DirectorySerializer()

    class Meta(object):
        model = models.File
        fields = ('id', 'uri', 'name', 'directory')


class FileHashSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    file = FileSerializer()
    version = VersionSerializer()
    device = DeviceSerializer()
    algorithm = AlgorithmSerializer()

    class Meta(object):
        model = models.FileHash
        fields = ('id', 'uri', 'file', 'version', 'device', 'size', 'algorithm',
                  'hash', 'mutable')
