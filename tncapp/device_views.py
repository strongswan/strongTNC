# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _

from . import models as tnc_models


@require_GET
@login_required
def devices(request):
    """
    All devices
    """
    context = {}
    context['title'] = _('Devices')
    return render(request, 'tncapp/devices.html', context)


@require_GET
@login_required
def device(request, deviceID):
    """
    Device detail view
    """
    try:
        device = tnc_models.Device.objects.get(pk=deviceID)
    except tnc_models.Device.DoesNotExist:
        device = None
        messages.error(request, _('Device not found!'))

    context = {}
    context['title'] = _('Devices')

    if device:
        context['device'] = device
        device_groups = device.groups.all().order_by('name')
        context['device_groups'] = device_groups
        context['products'] = tnc_models.Product.objects.all().order_by('name')

        groups = tnc_models.Group.objects.exclude(id__in=device_groups.values_list('id', flat=True))
        context['groups'] = groups
        context['title'] = _('Device ') + device.description

    return render(request, 'tncapp/devices.html', context)


@require_GET
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def add(request):
    """
    Add new device
    """
    context = {}
    context['title'] = _('New device')
    context['groups'] = tnc_models.Group.objects.all().order_by('name')
    context['products'] = tnc_models.Product.objects.all().order_by('name')
    context['device'] = tnc_models.Device()
    return render(request, 'tncapp/devices.html', context)


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def save(request):
    """
    Insert/update a device
    """
    deviceID = request.POST['deviceId']
    if not (deviceID == 'None' or re.match(r'^\d+$', deviceID)):
        return HttpResponse(status=400)

    device_groups = []
    if request.POST['memberlist'] != '':
        device_groups = request.POST['memberlist'].split(',')

    for member in device_groups:
        if not re.match(r'^\d+$', member):
            return HttpResponse(status=400)

    value = request.POST['value'].lower()
    if not re.match(r'^[a-f0-9]+$', value):
        return HttpResponse(status=400)

    description = request.POST['description']
    if not re.match(r'^[\S ]{0,50}$', description):
        return HttpResponse(status=400)

    productID = request.POST['product']
    if not re.match(r'^\d+$', productID):
        return HttpResponse(status=400)

    try:
        product = tnc_models.Product.objects.get(pk=productID)
    except tnc_models.Product.DoesNotExist:
        return HttpResponse(status=400)

    if deviceID == 'None':
        device = tnc_models.Device.objects.create(value=value, description=description,
                product=product, created=timezone.now())
    else:
        device = get_object_or_404(tnc_models.Device, pk=deviceID)
        device.value = value
        device.description = description
        device.product = product
        device.save()

    if device_groups:
        device.groups.clear()
        device_groups = tnc_models.Group.objects.filter(id__in=device_groups)
        for member in device_groups:
            device.groups.add(member)

        device.save()

    messages.success(request, _('Device saved!'))
    return redirect('/devices/%d' % device.id)


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def delete(request, deviceID):
    """
    Delete a device
    """
    device = get_object_or_404(tnc_models.Device, pk=deviceID)
    device.delete()

    messages.success(request, _('Device deleted!'))
    return redirect('/devices')


@require_GET
@login_required
def report(request, deviceID):
    """
    Generate device report for given device
    """
    device = get_object_or_404(tnc_models.Device, pk=deviceID)

    context = {}
    context['device'] = device
    context['title'] = _('Report for ') + str(device)

    sessions = tnc_models.Session.objects.filter(device=device).order_by('-time')
    context['session_count'] = len(sessions)
    context['definition_set'] = list(device.groups.all())
    context['inherit_set'] = list(device.get_inherit_set())

    if context['session_count'] > 0:
        context['sessions'] = []
        for session in sessions[:50]:
            context['sessions'].append((session,
                tnc_models.Policy.action[session.recommendation]))

        session = sessions.latest('time')
        context['last_session'] = session.time
        context['last_user'] = session.identity.data
        context['last_result'] = tnc_models.Policy.action[session.recommendation]
    else:
        context['last_session'] = _('Never')
        context['last_user'] = _('No one')
        context['last_result'] = _('N/A')

    enforcements = []
    for group in context['definition_set'] + context['inherit_set']:
        for e in group.enforcements.all():
            try:
                result = tnc_models.Result.objects.filter(
                        session__device=device, policy=e.policy).latest()
                enforcements.append((e, tnc_models.Policy.action[result.recommendation],
                    device.is_due_for(e)))
            except tnc_models.Result.DoesNotExist:
                enforcements.append((e, _('N/A'), True))

    context['enforcements'] = enforcements

    return render(request, 'tncapp/device_report.html', context)


@require_GET
@login_required
def session(request, sessionID):
    """
    View details for a device-session
    """
    session = get_object_or_404(tnc_models.Session, pk=sessionID)

    context = {}
    context['session'] = session
    context['title'] = _('Session details')
    context['recommendation'] = tnc_models.Policy.action[session.recommendation]

    context['results'] = []
    for result in session.results.all():
        context['results'].append((result, tnc_models.Policy.action[result.recommendation]))
        if result.policy.type == tnc_models.WorkItemType.SWIDT:
            context['swid_measurement'] = result.session_id

    return render(request, 'tncapp/session.html', context)


@require_GET
@login_required
def toggle_trusted(request, device_id):
    """
    Toggle the trusted state of a device
    """
    device_object = get_object_or_404(tnc_models.Device, pk=device_id)
    device_object.trusted = not device_object.trusted
    device_object.save()
    return HttpResponse(_('Yes' if device_object.trusted else 'No'))
