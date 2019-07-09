# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

try:
    from djangorestframework_camel_case.parser import camel_to_underscore
except ImportError:
    camel_to_underscore = lambda x: x


class DynamicFieldsMixin(object):
    """
    A serializer mixin that takes an additional `fields` argument that controls
    which fields should be displayed.

    If the djangorestframework_camel_case package is installed, the field names
    are converted from camelCase to under_scores.

    Usage::

        class MySerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
            class Meta(object):
                model = MyModel

    """
    def __init__(self, *args, **kwargs):
        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request:
            fields = request.query_params.get('fields')
            if fields:
                fields = fields.split(',')
                fields = map(camel_to_underscore, fields)
                # Drop any fields that are not specified in the `fields` argument.
                allowed = set(fields)
                existing = set(self.fields.keys())
                for field_name in existing - allowed:
                    self.fields.pop(field_name)
