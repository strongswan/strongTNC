# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re
from datetime import timedelta

from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_safe, require_http_methods
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.swid import utils as swid_utils
from apps.devices.models import Device, Group, Product
from apps.packages.models import Package
from tncapp.models import Session, Result, Action, Enforcement
from tncapp.models import Policy, WorkItem, WorkItemType


@require_GET
@login_required
def overview(request):
    """
    Main page
    """
    return render(request, 'tncapp/overview.html')


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


@require_GET
def statistics(request):
    """
    Statistics view
    """
    context = {}
    context['title'] = _('Statistics')
    context['sessions'] = Session.objects.count()
    context['results'] = Result.objects.count()
    context['enforcements'] = Enforcement.objects.count()
    context['devices'] = Device.objects.count()
    context['packages'] = Package.objects.count()
    context['products'] = Product.objects.count()
    context['OSranking'] = Product.objects.annotate(num=Count('devices__id')).order_by('-num')

    context['rec_count_session'] = Session.objects.values('recommendation').annotate(
            num=Count('recommendation')).order_by('-num')

    for item in context['rec_count_session']:
        item['recommendation'] = Policy.action[item['recommendation']]

    context['rec_count_result'] = Result.objects.values('recommendation').annotate(
            num=Count('recommendation')).order_by('-num')

    for item in context['rec_count_result']:
        item['recommendation'] = Policy.action[item['recommendation']]

    return render(request, 'tncapp/statistics.html', context)


@require_http_methods(('GET', 'POST'))
def login(request):
    """
    Login view
    """
    if request.method == 'POST':
        # Get login data from POST
        password = request.POST.get('password', None)
        username = request.POST.get('access_level', None)

        # Validate credentials
        if username not in ['admin-user', 'readonly-user']:
            # Make sure that people cannot log in as an arbitrary user
            # using faked HTTP requests.
            user = None
        else:
            # If authentication fails, the function returns ``None``.
            user = authenticate(username=username, password=password)

        # Authenticate user
        if user is not None and user.is_active:
                django_login(request, user)
                next_url = request.POST.get('next_url', None)
                if next_url is not None:
                    return redirect(next_url)
                else:
                    return redirect('/overview')
        else:
            messages.error(request, _('Bad password!'))

    if request.user.is_authenticated():
        return redirect('/overview')

    context = {'next_url': request.GET.get('next', '')}
    return render(request, 'tncapp/login.html', context)


def logout(request):
    """
    Logout and redirect to login view
    """
    django_logout(request)
    messages.success(request, _('Logout successful!'))

    return render(request, 'tncapp/login.html')


# NOT views, do not need decorators

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


def purge_dead_sessions():
    """
    Removes sessions that have not been ended after 7 days
    """
    MAX_AGE = 7  # days

    deadline = timezone.now() - timedelta(days=MAX_AGE)
    dead = Session.objects.filter(recommendation=None, time__lte=deadline)

    for d in dead:
        d.delete()


def import_swid_tags(session):
    workitem = WorkItem.objects.get(session=session, type=WorkItemType.SWIDT)
    result = workitem.result

    if not result:
        raise ValueError('No SWID tags provided')

    swid_tags = result.splitlines()

    for swid_tag in swid_tags:
        swid_utils.process_swid_tag(swid_tag.encode('utf-8'))
