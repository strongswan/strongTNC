# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json
from datetime import datetime

from dajaxice.decorators import dajaxice_register

from apps.core.decorators import ajax_login_required
from .models import Device


@dajaxice_register
@ajax_login_required
def sessions_for_device(request, device_id, date_from, date_to):
    dateobj_from, dateobj_to = map(datetime.utcfromtimestamp, [date_from, date_to])
    device = Device.objects.get(pk=device_id)
    sessions = device.sessions.filter(time__lte=dateobj_to, time__gte=dateobj_from)

    data = {'sessions': [
        {'id': s.id, 'time': s.time.strftime('%b %d %H:%M:%S %Y')}
        for s in sessions
    ]}

    return json.dumps(data)
