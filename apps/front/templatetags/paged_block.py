# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json

from django import template

register = template.Library()


@register.inclusion_tag('front/paged_block.html')
def paged_block(config_name, with_filter=False, producer_args=None):
    return {
        'config_name': config_name,
        'with_filter': with_filter,
        'producer_args': json.dumps(producer_args),
    }
