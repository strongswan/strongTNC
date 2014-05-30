# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def highlight(text, word):
    output = re.sub(r'(?i)(%s)' % re.escape(word), r'<span class="highlight">\1</span>', text)
    return mark_safe(output)
