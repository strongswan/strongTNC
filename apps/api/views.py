# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import viewsets

from apps.swid import models as swid_models

from . import serializers


class EntityViewSet(viewsets.ReadOnlyModelViewSet):
    model = swid_models.Entity
    serializer_class = serializers.EntitySerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    model = swid_models.Tag
    serializer_class = serializers.TagSerializer
