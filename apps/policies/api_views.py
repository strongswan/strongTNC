# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import viewsets

from . import models, serializers


class PolicyViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Policy
    serializer_class = serializers.PolicySerializer
