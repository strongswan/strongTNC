# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _

from apps.devices.models import Group
from .models import Enforcement, Policy


@require_GET
@login_required
def enforcements(request):
    """
    All enforcements
    """
    context = {}
    context['title'] = _('Enforcements')

    return render(request, 'policies/enforcements.html', context)


@require_GET
@login_required
def enforcement(request, enforcementID):
    """
    Enforcement detail view
    """
    try:
        enforcement = Enforcement.objects.get(pk=enforcementID)
    except Enforcement.DoesNotExist:
        enforcement = None
        messages.error(request, _('Enforcement not found!'))

    context = {}
    context['title'] = _('Enforcements')

    if enforcement:
        context['enforcement'] = enforcement
        groups = Group.objects.all().order_by('name')
        context['groups'] = groups
        context['actions'] = Policy.action
        context['title'] = _('Enforcement ') + str(enforcement)
        context['policies'] = Policy.objects.all().order_by('name')

    return render(request, 'policies/enforcements.html', context)


@require_GET
@login_required
@permission_required('auth.write_access', raise_exception=True)
def add(request):
    """
    Add new enforcement
    """
    context = {}
    context['title'] = _('New enforcement')
    context['count'] = Enforcement.objects.count()
    context['groups'] = Group.objects.all().order_by('name')
    context['policies'] = Policy.objects.all().order_by('name')
    enforcement = Enforcement()
    enforcement.max_age = 0
    context['enforcement'] = enforcement
    context['actions'] = Policy.action
    return render(request, 'policies/enforcements.html', context)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def save(request):
    """
    Insert/update an enforcement
    """
    enforcement_id = request.POST.get('enforcementId', '')
    if not (enforcement_id == 'None' or re.match(r'^\d+$', enforcement_id)):
        return HttpResponseBadRequest()

    max_age = request.POST.get('max_age', '')
    if not re.match(r'^\d+$', max_age):
        return HttpResponseBadRequest()

    policy_id = request.POST.get('policy', '')
    if not re.match(r'^\d+$', policy_id):
        return HttpResponseBadRequest()

    group_id = request.POST.get('group', '')
    if not re.match(r'^\d+$', group_id):
        return HttpResponseBadRequest()

    try:
        policy = Policy.objects.get(pk=policy_id)
        group = Group.objects.get(pk=group_id)
    except (Policy.DoesNotExist, Group.DoesNotExist):
        return HttpResponseBadRequest()

    fail = request.POST.get('fail')
    if not (re.match(r'^-?\d+$', fail) and int(fail) in range(-1, len(Policy.action))):
        return HttpResponseBadRequest()

    fail = int(fail)
    if fail == -1:
        fail = None

    noresult = request.POST.get('noresult', -1)
    if not (re.match(r'^-?\d+$', noresult) and int(noresult) in range(-1, len(Policy.action))):
        return HttpResponseBadRequest()

    noresult = int(noresult)
    if noresult == -1:
        noresult = None

    if enforcement_id == 'None':
        enforcement = Enforcement.objects.create(group=group, policy=policy,
                max_age=max_age, fail=fail, noresult=noresult)
    else:
        enforcement = get_object_or_404(Enforcement, pk=enforcement_id)
        enforcement.group = group
        enforcement.policy = policy
        enforcement.max_age = max_age
        enforcement.fail = fail
        enforcement.noresult = noresult
        enforcement.save()

    messages.success(request, _('Enforcement saved!'))
    return redirect('policies:enforcement_detail', enforcement.pk)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def check(request):
    """
    Check enforcement for uniqueness

    Used for form validation with jQuery validator,
    http://jqueryvalidation.org/remote-method/

    Returns:
    - true for valid enforcement name
    - false for invalid einforcement name
    """
    is_valid = False
    if request.is_ajax():
        policy_id = request.POST.get('policy')
        policy_id = int(policy_id) if policy_id != '' else -1
        group_id = request.POST.get('group')
        group_id = int(group_id) if group_id != '' else -1
        enforcement_id = request.POST.get('enforcement')
        if enforcement_id == 'None':
            enforcement_id = ''
        enforcement_id = int(enforcement_id) if enforcement_id != '' else -1

        try:
            e = Enforcement.objects.get(policy=policy_id, group=group_id)
            is_valid = (e.id == enforcement_id)
        except Enforcement.DoesNotExist:
            is_valid = True

    return HttpResponse(("%s" % is_valid).lower())


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def delete(request, enforcementID):
    """
    Delete an enforcement
    """
    enforcement = get_object_or_404(Enforcement, pk=enforcementID)
    enforcement.delete()

    messages.success(request, _('Enforcement deleted!'))
    return redirect('policies:enforcement_list')
