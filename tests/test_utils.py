# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from apps.front.utils import timestamp_local_to_utc


def test_timestamp_local_to_utc():
    # Assuming this timezone is Europe/Zurich.
    # This can be parametrized if https://github.com/pelme/pytest_django/issues/93 is resolved.
    assert timestamp_local_to_utc(1000000000) == 1000007200
