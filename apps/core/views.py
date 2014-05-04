# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re
from datetime import timedelta

from django.http import HttpResponse
from django.views.decorators.http import require_safe
from django.utils import timezone

from apps.core.models import Session, Result
from apps.core.types import Action
from apps.devices.models import Group


@require_safe
def start_session(request):
    """
    Initializes a new session and creates workitems according to policy
    """

    purge_dead_sessions()

    sessionID = request.GET.get('sessionID', '')
    if not re.match(r'^[0-9]+$', sessionID):
        return HttpResponse(status=400)

    try:
        session = Session.objects.get(pk=sessionID)
    except Session.DoesNotExist:
        return HttpResponse(status=404)

    device = session.device

    if not device.created:
        # This is a new device
        device.created = timezone.now()

        if device.product.default_groups.all():
            for group in device.product.default_groups.all():
                device.groups.add(group)
        else:
            # If no default groups for OS are specified
            device.groups.add(Group.objects.get(pk=1))

        device.save()

    device.create_work_items(session)

    return HttpResponse(content='')


@require_safe
def end_session(request):
    """
    End session and process results
    """
    sessionID = request.GET.get('sessionID', -1)

    try:
        session = Session.objects.get(pk=sessionID)
    except Session.DoesNotExist:
        return HttpResponse(status=404)

    generate_results(session)

    return HttpResponse(status=200)


def purge_dead_sessions():
    """
    Removes sessions that have not been ended after 7 days
    """
    MAX_AGE = 7  # days

    deadline = timezone.now() - timedelta(days=MAX_AGE)
    dead = Session.objects.filter(recommendation=None, time__lte=deadline)

    for d in dead:
        d.delete()


def generate_results(session):
    """
    Generates result from the sessions workitems and removes the workitems
    """
    workitems = session.workitems.all()

    for item in workitems:
        Result.objects.create(result=item.result, session=session,
                policy=item.enforcement.policy,
                recommendation=item.recommendation or Action.NONE)

    if workitems:
        session.recommendation = max(workitems, key=lambda x: x.recommendation)
    else:
        session.recommendation = Action.ALLOW

    session.save()

    for item in workitems:
        item.delete()
