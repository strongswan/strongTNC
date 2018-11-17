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

from apps.core.models import Session, Result
from apps.swid.models import Event, TagEvent
from .models import Device, Group, Product


@require_GET
@login_required
def devices(request):
    """
    All devices
    """
    context = {}
    context['title'] = _('Devices')
    return render(request, 'devices/devices.html', context)


@require_GET
@login_required
def device(request, deviceID):
    """
    Device detail view
    """
    try:
        device = Device.objects.get(pk=deviceID)
    except Device.DoesNotExist:
        device = None
        messages.error(request, _('Device not found!'))

    context = {}
    context['title'] = _('Devices')

    if device:
        context['device'] = device
        device_groups = device.groups.all().order_by('name')
        context['device_groups'] = device_groups
        context['products'] = Product.objects.all().order_by('name')

        groups = Group.objects.exclude(id__in=device_groups.values_list('id', flat=True))
        context['groups'] = groups
        context['title'] = _('Device ') + device.description

    return render(request, 'devices/devices.html', context)


@require_GET
@login_required
@permission_required('auth.write_access', raise_exception=True)
def add(request):
    """
    Add new device
    """
    context = {}
    context['title'] = _('New device')
    context['groups'] = Group.objects.all().order_by('name')
    context['products'] = Product.objects.all().order_by('name')
    context['device'] = Device()
    return render(request, 'devices/devices.html', context)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
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

    trusted = True if request.POST.get('device-trusted', False) == 'on' else False
    inactive = True if request.POST.get('device-inactive', False) == 'on' else False

    try:
        product = Product.objects.get(pk=productID)
    except Product.DoesNotExist:
        return HttpResponse(status=400)

    if deviceID == 'None':
        device = Device.objects.create(value=value, description=description,
                product=product, created=timezone.now(), trusted=trusted, inactive=inactive)
    else:
        device = get_object_or_404(Device, pk=deviceID)
        device.value = value
        device.description = description
        device.product = product
        device.trusted = trusted
        device.inactive = inactive
        device.save()

    if device_groups:
        device.groups.clear()
        device_groups = Group.objects.filter(id__in=device_groups)
        for member in device_groups:
            device.groups.add(member)

        device.save()

    messages.success(request, _('Device saved!'))
    return redirect('devices:device_detail', device.pk)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def delete(request, deviceID):
    """
    Delete a device
    """
    device = get_object_or_404(Device, pk=deviceID)
    device.delete()

    messages.success(request, _('Device deleted!'))
    return redirect('devices:device_list')


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def check(request):
    """
    Check devices for uniqueness

    Used for form validation with jQuery validator,
    http://jqueryvalidation.org/remote-method/

    Returns:
    - true for valid device name
    - false for invalid device name
    """
    is_valid = False
    if request.is_ajax():
        product_id = request.POST.get('product')
        product_id = int(product_id) if product_id != '' else -1
        device_value = request.POST.get('value')
        device_id = request.POST.get('device')
        if device_id == 'None':
            device_id = ''
        device_id = int(device_id) if device_id != '' else -1

        try:
            d = Device.objects.get(value=device_value, product=product_id)
            is_valid = (d.id == device_id)
        except Device.DoesNotExist:
            is_valid = True

    return HttpResponse(("%s" % is_valid).lower())


@require_GET
@login_required
def report(request, deviceID):
    """
    Generate device report for given device
    """
    current_device = get_object_or_404(Device, pk=deviceID)

    context = {}
    context['device'] = current_device
    context['title'] = _('Report for ') + str(current_device)
    context['paging_args'] = {'device_id': current_device.pk}

    context['session_count'] = Session.objects.filter(device=current_device).count()
    context['definition_set'] = list(current_device.groups.all())
    context['inherit_set'] = list(current_device.get_inherit_set())

    if context['session_count'] > 0:
        latest_session = Session.objects.filter(device=deviceID).latest()
        context['last_session'] = latest_session
        context['last_user'] = latest_session.identity.data
        context['last_result'] = latest_session.get_recommendation_display()
    else:
        context['last_session'] = False
        context['last_user'] = _('None')
        context['last_result'] = _('None')

    enforcements = []
    for group in context['definition_set'] + context['inherit_set']:
        for e in group.enforcements.all():
            try:
                result = Result.objects.filter(session__device=current_device, policy=e.policy).latest()
                enforcements.append((e, result.get_recommendation_display(),
                    current_device.is_due_for(e)))
            except Result.DoesNotExist:
                enforcements.append((e, _('None'), True))
    context['enforcements'] = enforcements

    context['installed_count'] = current_device.get_installed_count()
    context['vulnerability_count'] = current_device.get_vulnerabilities().count()

    return render(request, 'devices/device_report.html', context)


@require_GET
@login_required
def session(request, sessionID):
    """
    View details for a device-session
    """
    session = get_object_or_404(Session, pk=sessionID)

    context = {}
    context['session'] = session
    context['title'] = _('Session details')
    context['recommendation'] = session.get_recommendation_display()

    context['results'] = session.results.all()

    return render(request, 'devices/session.html', context)


@require_GET
@login_required
def event(request, eventID):
    """
    View details for a device-event
    """
    event = get_object_or_404(Event, pk=eventID)

    context = {}
    context['event'] = event
    context['title'] = _('Event details')
    context['tags'] = event.tags.all()
    context['tag_events'] = TagEvent.objects.filter(event=eventID)
    return render(request, 'devices/event.html', context)


@require_GET
@login_required
def toggle_trusted(request, device_id):
    """
    Toggle the trusted state of a device
    """
    device_object = get_object_or_404(Device, pk=device_id)
    device_object.trusted = not device_object.trusted
    device_object.save()
    return HttpResponse(_('Yes' if device_object.trusted else 'No'))


@require_GET
@login_required
def toggle_inactive(request, device_id):
    """
    Toggle the inactive state of a device
    """
    device_object = get_object_or_404(Device, pk=device_id)
    device_object.inactive = not device_object.inactive
    device_object.save()
    return HttpResponse(_('Yes' if device_object.inactive else 'No'))
