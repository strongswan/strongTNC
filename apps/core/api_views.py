# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import viewsets

from . import models, serializers


class IdentityViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Identity
    queryset = model.objects.all()
    serializer_class = serializers.IdentitySerializer
    filter_fields = ('type', 'data',)


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Session
    queryset = model.objects.all()
    serializer_class = serializers.SessionSerializer


class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Result
    queryset = model.objects.all()
    serializer_class = serializers.ResultSerializer
    filter_fields = ('session', 'policy')
