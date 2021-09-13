# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from apps.api.mixins import DynamicFieldsMixin
from . import models


class EventSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Event
        fields = ('id', 'uri', 'device', 'epoch', 'eid', 'timestamp', 'tags')


class EntitySerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Entity
        fields = ('id', 'uri', 'name', 'regid')


class EntityRoleSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.EntityRole
        fields = ('entity', 'role')


class TagEventSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.TagEvent
        fields = ('event', 'action', 'record_id', 'source_id')


class TagSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    entities = EntityRoleSerializer(source='entityrole_set', many=True)
    events = TagEventSerializer(source='tagevent_set', many=True)

    class Meta(object):
        model = models.Tag
        fields = ('id', 'uri', 'package_name', 'version_str', 'version', 'unique_id',
                  'software_id', 'entities', 'events', 'swid_xml')


class TagMiniSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):

    class Meta(object):
        model = models.Tag
        fields = ('id', 'uri', 'package_name', 'version_str', 'unique_id')


class TagStatsSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    tag = TagMiniSerializer()

    class Meta(object):
        model = models.TagStats
        fields = ('tag', 'device', 'first_seen', 'last_seen', 'first_installed', 'last_deleted')
