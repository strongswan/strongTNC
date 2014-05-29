# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json

from dajaxice.decorators import dajaxice_register

from apps.core.decorators import ajax_login_required
from .models import Device
from apps.front.utils import local_dtstring


@dajaxice_register
@ajax_login_required
def sessions_for_device(request, device_id, date_from, date_to):
    device = Device.objects.get(pk=device_id)
    sessions = device.get_sessions_in_range(date_from, date_to)

    data = {
        'sessions': [
            {
                'id': s.id,
                'time': local_dtstring(s.time)
            }
            for s in sessions
        ]
    }

    return json.dumps(data)
