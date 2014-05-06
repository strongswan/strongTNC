# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from apps.swid import models as swid_models


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = swid_models.Entity
        fields = ('id', 'name', 'regid')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = swid_models.Tag
        fields = ('id', 'package_name', 'version', 'unique_id', 'swid_xml')
