# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from apps.api.mixins import DynamicFieldsMixin
from . import models


class EntitySerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Entity
        fields = ('id', 'uri', 'name', 'regid')


class EntityRoleSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.EntityRole
        fields = ('entity', 'role')


class TagSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    entities = EntityRoleSerializer(source='entityrole_set', many=True)

    class Meta(object):
        model = models.Tag
        fields = ('id', 'uri', 'package_name', 'version', 'unique_id', 'entities', 'swid_xml')
