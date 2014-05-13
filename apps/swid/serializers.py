# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from . import models


class EntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Entity
        fields = ('id', 'uri', 'name', 'regid')


class TagSerializer(serializers.HyperlinkedModelSerializer):
    entity_set = serializers.HyperlinkedRelatedField(many=True, view_name='entity-detail')

    class Meta:
        model = models.Tag
        fields = ('id', 'uri', 'package_name', 'version', 'unique_id', 'entity_set', 'swid_xml')
