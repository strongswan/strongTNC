# -*- coding: utf-8 -*-
"""
Helper functions used for API-related tasks.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework.response import Response


def make_message(message, status_code):
    """
    Generate and return an API Response.

    Args:
        message:
            The message to be returned in the response.
        status_code:
            The HTTP status code for the response.

    Returns:
        A :class:`rest_framework.response.Response` instance.

    """
    return Response({'detail': message}, status=status_code)
