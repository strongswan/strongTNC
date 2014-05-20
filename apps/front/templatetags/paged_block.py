# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django import template

register = template.Library()


@register.inclusion_tag('front/paged_block.html')
def paged_block(template_name, list_producer, stat_producer,
                var_name, page_size, url_name='', with_filter=False):
    return {
        'template_name': template_name,
        'list_producer': list_producer,
        'stat_producer': stat_producer,
        'var_name': var_name,
        'url_name': url_name,
        'page_size': page_size,
        'with_filter': with_filter
    }
