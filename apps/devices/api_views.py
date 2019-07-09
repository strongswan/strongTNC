# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import viewsets

from . import models, serializers


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Product
    queryset = model.objects.all()
    serializer_class = serializers.ProductSerializer
    filter_fields = ('name',)


class DeviceViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Device
    queryset = model.objects.all()
    serializer_class = serializers.DeviceSerializer
    filter_fields = ('value', 'description', 'product', 'created', 'trusted', 'inactive',)
