# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json

from django import template

register = template.Library()


@register.inclusion_tag('front/paged_block.html')
def paged_block(config_name, with_filter=False, producer_args=None, initial_load=True, use_url_params=True):
    return {
        'config_name': config_name,
        'with_filter': with_filter,
        'initial_load': initial_load,
        'use_url_params': use_url_params,
        'producer_args': json.dumps(producer_args),
    }
