# -*- coding: utf-8 -*-
"""
Tests for `swid` app.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

from datetime import datetime
from calendar import timegm

from django.utils.timezone import get_current_timezone, utc

from model_mommy import mommy

from apps.core.models import Session
from apps.devices.models import Device


def test_get_sessions_in_range(transactional_db):

    def unix_timestamp(dt):
        return timegm(dt.utctimetuple())

    tz = get_current_timezone()
    dt1 = datetime(2014, 1, 1, 0, 0, 0, tzinfo=utc)
    dt2 = datetime(2014, 1, 1, 14, 0, 0, tzinfo=utc)
    dt3 = datetime(2014, 1, 1, 23, 59, 59, tzinfo=utc)
    dt4 = datetime(2014, 1, 2, 0, 0, 0, tzinfo=utc)

    d = mommy.make(Device)
    mommy.make(Session, device=d, time=dt1)
    mommy.make(Session, device=d, time=dt2)
    mommy.make(Session, device=d, time=dt3)
    mommy.make(Session, device=d, time=dt4)

    s1 = d.get_sessions_in_range(unix_timestamp(dt1), unix_timestamp(dt1))
    assert len(s1) == 3
    s2 = d.get_sessions_in_range(unix_timestamp(dt1), unix_timestamp(dt2))
    assert len(s2) == 3
    s3 = d.get_sessions_in_range(unix_timestamp(dt1), unix_timestamp(dt3))
    assert len(s3) == 3
    s4 = d.get_sessions_in_range(unix_timestamp(dt1), unix_timestamp(dt4))
    assert len(s4) == 4
    s5 = d.get_sessions_in_range(unix_timestamp(dt3), unix_timestamp(dt4))
    assert len(s5) == 4
