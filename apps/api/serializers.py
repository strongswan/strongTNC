# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from apps.swid import models as swid_models


class EntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = swid_models.Entity
        fields = ('id', 'url', 'name', 'regid')


class TagSerializer(serializers.HyperlinkedModelSerializer):
    entity_set = serializers.HyperlinkedRelatedField(many=True, view_name='entity-detail')

    class Meta:
        model = swid_models.Tag
        fields = ('id', 'url', 'package_name', 'version', 'unique_id', 'entity_set', 'swid_xml')
