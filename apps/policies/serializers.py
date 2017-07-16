# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from apps.api.mixins import DynamicFieldsMixin
from . import models


class PolicySerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Policy
        fields = ('id', 'uri', 'type', 'name', 'argument', 'fail', 'noresult')
