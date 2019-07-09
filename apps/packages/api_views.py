# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import viewsets

from . import models, serializers


class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Package
    queryset = model.objects.all()
    serializer_class = serializers.PackageSerializer
    filter_fields = ('name',)


class VersionViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Version
    queryset = model.objects.all()
    serializer_class = serializers.VersionSerializer
    filter_fields = ('package', 'product', 'release', 'security', 'blacklist', 'time',)
