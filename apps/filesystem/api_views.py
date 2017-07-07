# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import viewsets

from . import models, serializers


class AlgorithmViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Algorithm
    serializer_class = serializers.AlgorithmSerializer
    filter_fields = ('name',)


class DirectoryViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Directory
    serializer_class = serializers.DirectorySerializer
    filter_fields = ('path',)


class FileViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.File
    serializer_class = serializers.FileSerializer
    filter_fields = ('name', 'directory', 'directory__path',)


class FileHashViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.FileHash
    serializer_class = serializers.FileHashSerializer
    filter_fields = ('file', 'file__name', 'file__directory__path', 'version',
                     'device', 'size', 'algorithm', 'hash', 'mutable',)
