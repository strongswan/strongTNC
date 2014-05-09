# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def input_editability(context):
    perms = context.get('perms', [])
    if 'auth.write_access' not in perms:
        return 'disabled="disabled"'
    return ''
