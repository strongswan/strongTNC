# -*- coding: utf-8 -*-
"""
Migration script for issue 294: https://github.com/tnc-ba/strongTNC/pull/294
"""
from __future__ import print_function, division, absolute_import, unicode_literals

from apps.core.models import Session
from apps.swid.utils import update_tag_stats


for session in Session.objects.all().order_by('time'):
    print('Processing session %d...' % session.pk)
    tag_ids = session.tag_set.values_list('pk', flat=True)
    update_tag_stats(session, tag_ids)

print('Done.')
