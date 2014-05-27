# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from . import models


class EntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Entity
        fields = ('id', 'uri', 'name', 'regid')


class EntityRoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.EntityRole
        fields = ('entity', 'role')


class TagSerializer(serializers.HyperlinkedModelSerializer):
    entities = EntityRoleSerializer(source='entityrole_set', many=True)

    class Meta:
        model = models.Tag
        fields = ('id', 'uri', 'package_name', 'version', 'unique_id', 'entities', 'swid_xml')
