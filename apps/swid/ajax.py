# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json
from collections import Counter

from dajaxice.decorators import dajaxice_register

from apps.core.decorators import ajax_login_required
from apps.core.models import Session
from apps.devices.models import Device
from apps.front.utils import local_dtstring
from .models import Tag
from .paging import get_tag_diffs


@dajaxice_register
@ajax_login_required
def get_tag_inventory_stats(request, device_id, from_timestamp, to_timestamp):
    """
    Return some figures regarding the number of sessions in a given
    given timerange.

    Args:
        device_id (int/str):
            A device id, might be provided as int or string (javascript)

        from_timestamp (int):
            Start time of the range, in Unix time

        to_timestamp (int):
            Last time of the range, in Unix time

    Returns:
        A JSON object in the following format (example data):
            {
                "session_count": 8,
                "latest_session": Nov 20 10:22:12 2013,
                "oldes_session": Jan 30 11:14:34 2012,
            }

    """
    data = {
        'session_count': 0,
        'last_session': 'None',
        'fist_session': 'None',
    }

    try:
        device = Device.objects.get(pk=device_id)
    except Session.DoesNotExist:
        return json.dumps(data)

    sessions = device.get_sessions_in_range(from_timestamp, to_timestamp).order_by('time')
    if sessions:
        data = {
            'session_count': sessions.count(),
            'last_session': local_dtstring(sessions.last().time),
            'fist_session': local_dtstring(sessions.first().time),
        }

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
        return json.dumps({
            'session_count': 0,
            'first_session': 'None',
            'last_session': 'None',
            'added_count': 0,
            'removed_count': 0,
        })


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
