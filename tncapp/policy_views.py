#
# Copyright (C) 2013 Marco Tanner
# Copyright (C) 2013 Stefan Rohner
# HSR University of Applied Sciences Rapperswil
#
# This file is part of strongTNC.  strongTNC is free software: you can
# redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# strongTNC is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with strongTNC.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Provides CRUD for policies
"""

import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import Policy, Group, File, Directory


@require_GET
@login_required
def policies(request):
    """
    All policies
    """
    context = {}
    context['title'] = _('Policies')
    context['count'] = Policy.objects.count()
    policies = Policy.objects.all().order_by('name')

    context['policies'] = paginate(policies, request)
    return render(request, 'tncapp/policies.html', context)


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
    context['count'] = Policy.objects.count()
    policies = Policy.objects.all().order_by('name')

    context['policies'] = paginate(policies, request)

    if policy:
        context['policy'] = policy
        enforcements = policy.enforcements.all().order_by('id')
        context['enforcements'] = enforcements
        context['types'] = Policy.types
        for typ in context['types']:
            typ = _(typ)
        context['action'] = Policy.action
        files = File.objects.all().order_by('name')
        context['files'] = files
        dirs = Directory.objects.all().order_by('path')
        context['dirs'] = dirs

        groups = Group.objects.exclude(id__in=enforcements.values_list('id', flat=True))
        context['groups'] = groups
        context['title'] = _('Policy ') + policy.name

    return render(request, 'tncapp/policies.html', context)


@require_GET
@login_required
def add(request):
    """
    Add new policy
    """
    context = {}
    policies = Policy.objects.all().order_by('name')
    context['policies'] = paginate(policies, request)
    context['title'] = _('New policy')
    context['count'] = Policy.objects.count()
    context['types'] = Policy.types
    context['action'] = Policy.action
    context['policy'] = Policy()
    files = File.objects.all().order_by('name')
    context['files'] = files
    dirs = Directory.objects.all().order_by('path')
    context['dirs'] = dirs
    return render(request, 'tncapp/policies.html', context)


@require_POST
@login_required
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
        #TODO: flip does not exist in the policy form (view), is this save to delete?
        flip = unicode(request.POST.get('flip')).lower() in ['1', 'yes', 'y', 'true']
        if ranges is not '' and ranges is not None:
            if not check_range(ranges):
                raise ValueError('Port ranges are not valid.')

            if flip:
                ranges = invert_range(ranges)

            argument = normalize_ranges_whitespace(ranges)

    # swid tag inventory
    elif policy_type == 15:
        swid_flag = request.POST.get('flags', None)
        if swid_flag in Policy.swid_request_flags:
            argument = swid_flag
            print argument
        else:
            raise ValueError('SWID flag is not valid.')

    # tpm remote attestation
    elif policy_type == 16:
        tmp_flag = request.POST.get('flags', None)
        if tmp_flag in Policy.tpm_attestation_flags:
            argument = tmp_flag
        else:
            raise ValueError('TMP attestation flag is not valid.')

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
        policy = Policy(name=name, type=policy_type, fail=fail, noresult=noresult, file=file, dir=dir,
                        argument=argument)
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
    return redirect('/policies/%d' % policy.id)


@require_POST
@login_required
def check(request):
    """
    Check if policy name is unique
    """
    response = False
    if request.is_ajax():
        policy_name = request.POST['name']
        policy_id = request.POST['policy']
        if policy_id == 'None':
            policy_id = ''

        try:
            policy = Policy.objects.get(name=policy_name)
            response = (str(policy.id) == policy_id)
        except Policy.DoesNotExist:
            response = True

    return HttpResponse(("%s" % response).lower())


@require_POST
@login_required
def delete(request, policy_id):
    """
    Delete a policy
    """
    policy = get_object_or_404(Policy, pk=policy_id)
    policy.delete()

    messages.success(request, _('Policy deleted!'))
    return redirect('/policies')


@require_GET
@login_required
def search(request):
    """
    Filter policies
    """
    context = {}
    context['title'] = _('Policies')
    context['count'] = Policy.objects.count()
    policies = Policy.objects.all().order_by('name')

    q = request.GET.get('q', None)
    if q != '':
        context['query'] = q
        policies = Policy.objects.filter(name__icontains=q)
    else:
        return redirect('/policies')

    context['policies'] = paginate(policies, request)
    return render(request, 'tncapp/policies.html', context)


def normalize_ranges_whitespace(ranges):
    """
    Reduce multiple whitespace-chars to exactly one space.

    Args:
        ranges:
            String containing port ranges.

    """
    return re.sub('\s+', ' ', ranges.strip())


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
            if not re.match('^\d+$', b):
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


def invert_range(ranges):
    """
    Inverts a given port range and inverts it to select all other ports
    Combines adjacent ports to ranges and sorts numerically
    """
    ranges = ranges.replace(' ', '')

    #Very special cases
    if ranges == '0-65535': return ''
    if ranges == '': return '0-65535'

    doubles = []
    for r in ranges.split(','):
        bounds = r.split('-', 1)
        lower = int(bounds[0])
        upper = int(bounds[1]) if len(bounds) > 1 else -1

        if upper != -1:
            doubles.append((lower, upper))
        else:
            doubles.append((lower, lower))

    doubles.sort(reverse=True)
    ranges = []

    while len(doubles) > 0:
        d = doubles.pop()
        lower = int(d[0])
        upper = int(d[1])

        if len(ranges) == 0 and lower != 0:
            if lower != 1:
                ranges.append('0-%d' % (lower - 1))
            else:
                ranges.append('0')

        while len(doubles) > 0 and upper >= int(doubles[-1][0] - 1):
            d2 = doubles.pop()
            if int(d2[1]) > upper:
                upper = int(d2[1])

        if len(doubles) > 0:
            if (upper + 1) != (doubles[-1][0] - 1):
                ranges.append('%d-%d' % (upper + 1, doubles[-1][0] - 1))
            else:
                ranges.append('%d' % (upper + 1))
        else:
            if upper != 65535:
                ranges.append('%d-65535' % (upper + 1))

    return ','.join(ranges)


def paginate(items, request):
    """
    Paginated browsing
    """
    paginator = Paginator(items, 50) # Show 50 policies per page
    page = request.GET.get('page')
    try:
        policies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        policies = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        policies = paginator.page(paginator.num_pages)

    return policies
