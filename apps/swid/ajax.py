# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json
from collections import Counter

from dajaxice.decorators import dajaxice_register

from apps.core.decorators import ajax_login_required
from apps.core.models import Session
from apps.front.utils import local_dtstring
from .models import Tag
from .paging import get_tag_diffs


@dajaxice_register
@ajax_login_required
def get_tag_stats(request, session_id):
    """
    Return some figures regarding installed SWID tags based on a
    given session.

    Args:
        session_id (int/str):
            A session id, might be provided as int or string (javascript)

    Returns:
        A JSON object in the following format (example data):
            {
                "swid-tag-count": 98,
                "new-swid-tag-count": 23
            }

    """
    try:
        session = Session.objects.get(pk=session_id)
    except Session.DoesNotExist:
        return json.dumps({})

    installed_tags = Tag.get_installed_tags_with_time(session)
    tag_counter = Counter(session.pk for session in installed_tags.values())
    new_tags_count = tag_counter[int(session_id)]
    data = {'swid-tag-count': len(installed_tags), 'new-swid-tag-count': new_tags_count}
    return json.dumps(data)


@dajaxice_register
@ajax_login_required
def get_tag_log_stats(request, device_id, from_timestamp, to_timestamp):
    """
    Return some figures regarding SWID tags history of given device
    in a given timerange.

    Args:
        device_id (int):

        from_timestamp (int):
            Start time of the range, in Unix time

        to_timestamp (int):
            Last time of the range, in Unix time

    Returns:
        A JSON object in the following format (example data):
        {
            "session_count": 4,
            "first_session": "Nov 17 10:22:12 2014",
            "last_session": "Nov 20 10:22:12 2014",
            "added_count": 99,
            "removed_count": 33
        }

    """
    diffs = get_tag_diffs(device_id, from_timestamp, to_timestamp)
    if diffs:
        added_count = 0
        removed_count = 0
        sessions = set()
        for diff in diffs:
            sessions.add(diff.session)
            if diff.action == '+':
                added_count += 1
            else:
                removed_count += 1

        s = sorted(sessions, key=lambda sess: sess.time)
        first_session = s[0]
        last_session = s[-1]

        result = {
            'session_count': len(sessions),
            'first_session': local_dtstring(first_session.time),
            'last_session': local_dtstring(last_session.time),
            'added_count': added_count,
            'removed_count': removed_count,
        }

        return json.dumps(result)
    else:
        return json.dumps({})


@dajaxice_register
@ajax_login_required
def session_info(request, session_id):
    try:
        session = Session.objects.get(pk=session_id)
    except Session.DoesNotExist:
        return json.dumps({})

    detail = {
        'id': session.pk,
        'time': local_dtstring(session.time)
    }

    return json.dumps(detail)
