# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import viewsets

from . import models, serializers


class IdentityViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Identity
    serializer_class = serializers.IdentitySerializer
    filter_fields = ('type', 'data',)


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Session
    serializer_class = serializers.SessionSerializer
