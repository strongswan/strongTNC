# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.timezone import localtime

from dajaxice.decorators import dajaxice_register

from apps.core.decorators import ajax_login_required
from apps.core.models import Session
from .models import Tag
from apps.devices.models import Device


@dajaxice_register
@ajax_login_required
def tags_for_session(request, session_id):
    try:
        session = Session.objects.get(pk=session_id)
    except Session.DoesNotExist:
        return json.dumps({})

    installed_tags = Tag.get_installed_tags_with_time(session)
    tags = [
        {
            'name': tag.package_name,
            'version': tag.version,
            'unique-id': tag.unique_id,
            'installed': localtime(session.time).strftime(settings.DEFAULT_DATETIME_FORMAT_STRING),
            'session-id': session.pk,
            'tag-url': reverse('swid:tag_detail', args=[tag.pk]),
        }
        for tag, session in installed_tags
    ]
    data = {'swid-tag-count': len(tags), 'swid-tags': tags}
    return json.dumps(data)


@dajaxice_register()
def get_tag_log(request, device_id, from_timestamp, to_timestamp):
    device = Device.objects.get(pk=device_id)
    sessions = device.get_sessions_in_range(from_timestamp, to_timestamp)

    sessions_with_tags = sessions.filter(tag__isnull=False).distinct().order_by('-time')

    diffs = []
    if len(sessions_with_tags) > 1:
        for i, session in enumerate(sessions_with_tags, start=1):
            if i < len(sessions_with_tags):
                prev_session = sessions_with_tags[i]
                diff = session_tag_difference(session, prev_session)
                diffs.append(diff)

        result = [
            {
                'session_id': d['session'].pk,
                'session_date': localtime(d['session'].time).strftime(
                    settings.DEFAULT_DATETIME_FORMAT_STRING),
                'added_tags': [{'unique_id': t.unique_id, 'tag_id': t.pk} for t in d['added_tags']],
                'removed_tags': [{'unique_id': t.unique_id, 'tag_id': t.pk} for t in d['removed_tags']],
                'tag_count': len(d['added_tags']) + len(d['removed_tags']),
            }
            for d in diffs
        ]
        return json.dumps(result)
    else:
        return json.dumps([])


def session_tag_difference(curr_session, prev_session):
    curr_tag_ids = curr_session.tag_set.values_list('id', flat=True).order_by('id')
    prev_tag_ids = prev_session.tag_set.values_list('id', flat=True).order_by('id')

    added_ids = list(set(curr_tag_ids) - set(prev_tag_ids))
    removed_ids = list(set(prev_tag_ids) - set(curr_tag_ids))

    added_tags = Tag.objects.filter(id__in=added_ids)
    removed_tags = Tag.objects.filter(id__in=removed_ids)

    return {
        'session': curr_session,
        'added_tags': added_tags,
        'removed_tags': removed_tags
    }


@dajaxice_register()
def session_info(request, session_id):
    try:
        session = Session.objects.get(pk=session_id)
    except Session.DoesNotExist:
        return json.dumps({})

    detail = {'id': session.pk,
              'time': localtime(session.time).strftime('%b %d %H:%M:%S %Y')}

    return json.dumps(detail)