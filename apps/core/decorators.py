# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from functools import wraps


class AuthenticationRequiredError(RuntimeError):
    pass


def ajax_login_required(func):
    @wraps(func)
    def __wrapper(request, *args, **kwargs):
        # Check authentication
        if not request.user.is_authenticated():
            raise AuthenticationRequiredError()
        return func(request, *args, **kwargs)
    return __wrapper
