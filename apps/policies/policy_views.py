# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re

from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _

from apps.filesystem.models import File, Directory
from .models import Policy


@require_GET
@login_required
def policies(request):
    """
    All policies
    """
    context = {}
    context['title'] = _('Policies')
    return render(request, 'policies/policies.html', context)


@require_GET
@login_required
def policy(request, policyID):
    """
    Policy detail view
    """
    try:
        policy = Policy.objects.get(pk=policyID)
    except Policy.DoesNotExist:
        policy = None
        messages.error(request, _('Policy not found!'))

    context = {}
    context['title'] = _('Policies')

    if policy:
        context['policy'] = policy
        context['types'] = Policy.types
        context['action'] = Policy.action
        try:
            context['file'] = policy.file
        except File.DoesNotExist:
            pass

        try:
            context['dir'] = policy.dir
        except Directory.DoesNotExist:
            pass

        enforcements = policy.enforcements.all()
        context['enforcements'] = enforcements
        if enforcements.count():
            context['has_dependencies'] = True

        context['title'] = _('Policy ') + policy.name

    return render(request, 'policies/policies.html', context)


@require_GET
@login_required
@permission_required('auth.write_access', raise_exception=True)
def add(request):
    """
    Add new policy
    """
    context = {}
    context['title'] = _('New policy')
    context['count'] = Policy.objects.count()
    context['types'] = Policy.types
    context['action'] = Policy.action
    context['policy'] = Policy()
    return render(request, 'policies/policies.html', context)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def save(request):
    """
    Insert/update a policy
    """
    policy_id = request.POST['policyId']
    if not (policy_id == 'None' or re.match(r'^\d+$', policy_id)):
        raise ValueError

    policy_type = request.POST['type']
    if not re.match(r'^\d+$', policy_type) and int(policy_type) in range(len(Policy.types)):
        raise ValueError

    policy_type = int(policy_type)

    file_id = request.POST.get('file', '')
    file = None
    if not file_id == '':
        if not re.match(r'^\d+$', file_id):
            raise ValueError

        try:
            file = File.objects.get(pk=file_id)
        except File.DoesNotExist:
            messages.warning(request, _('No such file'))

    dir_id = request.POST.get('dir', '')
    dir = None
    if not dir_id == '':
        if not re.match(r'^\d+$', dir_id):
            raise ValueError

        try:
            dir = Directory.objects.get(pk=dir_id)
        except Directory.DoesNotExist:
            messages.warning(request, _('No such directory'))

    argument = ''

    # port ranges
    if policy_type in [11, 12, 13, 14]:
        ranges = request.POST.get('range')
        if ranges != '' and ranges is not None:
            if not check_range(ranges):
                raise ValueError('Port ranges are not valid.')

            argument = normalize_ranges_whitespace(ranges)

    # swid tag inventory
    elif policy_type == 15:
        swid_flag = request.POST.get('flags', '').split()
        if set(swid_flag).issubset(Policy.swid_request_flags):
            argument = ' '.join(swid_flag)
        else:
            raise ValueError('SWID flags are not valid.')

    # tpm remote attestation
    elif policy_type == 16:
        tpm_flag = request.POST.get('flags', '').split()
        if set(tpm_flag).issubset(set(Policy.tpm_attestation_flags)):
            argument = ' '.join(tpm_flag)
        else:
            raise ValueError('TPM attestation flags are not valid.')

    fail = request.POST.get('fail')
    if not re.match(r'^\d+$', fail) and int(fail) in range(len(Policy.action)):
        raise ValueError('The value for the fail action is invalid.')

    noresult = request.POST['noresult']
    if not (re.match(r'^\d+$', noresult) and int(noresult) in range(len(Policy.action))):
        raise ValueError('The value for the noresult action is invalid.')

    name = request.POST['name']
    if not re.match(r'^[\S ]+$', name):
        raise ValueError('The policy name is invalid.')

    if policy_id == 'None':
        policy = Policy(name=name, type=policy_type, fail=fail, noresult=noresult,
                        file=file, dir=dir, argument=argument)
    else:
        policy = get_object_or_404(Policy, pk=policy_id)
        policy.name = name
        policy.type = policy_type
        policy.file = file
        policy.dir = dir
        policy.fail = fail
        policy.noresult = noresult

    policy.argument = argument
    type_name = Policy.types[policy.type]
    arg_func = Policy.argument_funcs[type_name]
    policy.argument = arg_func(policy)
    policy.save()

    messages.success(request, _('Policy saved!'))
    return redirect('policies:policy_detail', policy.pk)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def check(request):
    """
    Check if policy name is unique

    Used for form validation with jQuery validator,
    http://jqueryvalidation.org/remote-method/

    Returns:
    - true for valid policy name
    - false for invalid policy name

    """
    is_valid = False
    if request.is_ajax():
        policy_name = request.POST.get('name')
        policy_id = request.POST.get('policy')

        try:
            policy_obj = Policy.objects.get(name=policy_name)
            is_valid = (str(policy_obj.id) == policy_id)
        except Policy.DoesNotExist:
            is_valid = True

    return HttpResponse(("%s" % is_valid).lower())


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def delete(request, policyID):
    """
    Delete a policy
    """
    policy = get_object_or_404(Policy, pk=policyID)
    policy.delete()

    messages.success(request, _('Policy deleted!'))
    return redirect('policies:policy_list')


def normalize_ranges_whitespace(ranges):
    """
    Reduce multiple whitespace-chars to exactly one space.

    Args:
        ranges:
            String containing port ranges.

    """
    return re.sub(r'\s+', ' ', ranges.strip())


def check_range(ranges):
    """
    Check range input
    """
    if ranges == '':
        return True

    ranges = normalize_ranges_whitespace(ranges)
    for r in ranges.split():
        bounds = r.split('-', 1)
        for b in bounds:
            if not re.match(r'^\d+$', b):
                return False

        lower = int(bounds[0])
        upper = int(bounds[1]) if len(bounds) > 1 else -1

        if upper == -1:
            if not 0 <= lower <= 65535:
                return False
        else:
            if (not 0 <= upper <= 65535) or lower > upper:
                return False
    return True
