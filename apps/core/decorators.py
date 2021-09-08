# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from functools import wraps
from django.core.exceptions import PermissionDenied


def ajax_login_required(func):
    @wraps(func)
    def __wrapper(request, *args, **kwargs):
        # Check authentication
        if not request.user.is_authenticated:
            raise PermissionDenied()
        return func(request, *args, **kwargs)
    return __wrapper
