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
Provides CRUD for enforcements
"""

import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from models import Group, Enforcement, Policy


@require_GET
@login_required
def enforcements(request):
    """
    All enforcements
    """
    context = {}
    context['title'] = _('Enforcements')
    context['count'] = Enforcement.objects.count()
    enforcements = Enforcement.objects.all().order_by('policy')
    context['enforcements'] = paginate(enforcements, request)

    return render(request, 'tncapp/enforcements.html', context)


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
    context['count'] = Enforcement.objects.count()
    enforcements = Enforcement.objects.all().order_by('policy')
    context['enforcements'] = paginate(enforcements, request)

    if enforcement:
        context['enforcement'] = enforcement
        groups = Group.objects.all().order_by('name')
        context['groups'] = groups
        context['actions'] = Policy.action
        context['title'] = _('Enforcement ') + str(enforcement)
        context['policies'] = Policy.objects.all().order_by('name')

    return render(request, 'tncapp/enforcements.html', context)


@require_GET
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def add(request):
    """
    Add new enforcement
    """
    context = {}
    context['title'] = _('New enforcement')
    context['count'] = Enforcement.objects.count()
    context['groups'] = Group.objects.all().order_by('name')
    context['policies'] = Policy.objects.all().order_by('name')
    enforcements = Enforcement.objects.all().order_by('policy')
    context['enforcements'] = paginate(enforcements, request)
    enforcement = Enforcement()
    enforcement.max_age = 0
    context['enforcement'] = enforcement
    context['actions'] = Policy.action
    return render(request, 'tncapp/enforcements.html', context)


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def save(request):
    """
    Insert/udpate an enforcement
    """
    enforcementID = request.POST['enforcementId']
    if not (enforcementID == 'None' or re.match(r'^\d+$', enforcementID)):
        raise ValueError
        return HttpResponse(status=400)

    max_age = request.POST['max_age']
    if not re.match(r'^\d+$', max_age):
        raise ValueError
        return HttpResponse(status=400)

    policyID = request.POST['policy']
    if not re.match(r'^\d+$', policyID):
        raise ValueError
        return HttpResponse(status=400)

    groupID = request.POST['group']
    if not re.match(r'^\d+$', groupID):
        raise ValueError
        return HttpResponse(status=400)

    try:
        policy = Policy.objects.get(pk=policyID)
        group = Group.objects.get(pk=groupID)
    except (Policy.DoesNotExist, Group.DoesNotExist):
        raise ValueError
        return HttpResponse(status=400)

    fail = request.POST.get('fail')
    if not (re.match(r'^-?\d+$', fail) and int(fail) in range(-1, len(Policy.action))):
        # TODO replace lines like these with
        # raise HttpResponseBadRequest()
        raise ValueError
        return HttpResponse(status=400)

    fail = int(fail)
    if fail == -1:
        fail = None

    noresult = request.POST.get('noresult', -1)
    if not (re.match(r'^-?\d+$', noresult) and int(noresult) in range(-1, len(Policy.action))):
        raise ValueError
        return HttpResponse(status=400)

    noresult = int(noresult)
    if noresult == -1:
        noresult = None

    if enforcementID == 'None':
        enforcement = Enforcement.objects.create(group=group, policy=policy,
                max_age=max_age, fail=fail, noresult=noresult)
    else:
        enforcement = get_object_or_404(Enforcement, pk=enforcementID)
        enforcement.group = group
        enforcement.policy = policy
        enforcement.max_age = max_age
        enforcement.fail = fail
        enforcement.noresult = noresult
        enforcement.save()

    messages.success(request, _('Enforcement saved!'))
    return redirect('/enforcements/%d' % enforcement.id)


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def check(request):
    """
    Check enforcement for uniqueness
    """
    response = False
    if request.is_ajax():
        policy_id = request.POST['policy']
        policy_id = int(policy_id) if policy_id != '' else -1
        group_id = request.POST['group']
        group_id = int(group_id) if group_id != '' else -1
        enforcement_id = request.POST['enforcement']
        if enforcement_id == 'None':
            enforcement_id = ''
        enforcement_id = int(enforcement_id) if enforcement_id != '' else -1

        try:
            e = Enforcement.objects.get(policy=policy_id, group=group_id)

            response = (e.id == enforcement_id)
        except Enforcement.DoesNotExist:
            response = True

    return HttpResponse(("%s" % response).lower())


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def delete(request, enforcementID):
    """
    Delete an enforcement
    """
    enforcement = get_object_or_404(Enforcement, pk=enforcementID)
    enforcement.delete()

    messages.success(request, _('Enforcement deleted!'))
    return redirect('/enforcements')


@require_GET
@login_required
def search(request):
    """
    Filter enforcements
    """
    context = {}
    context['title'] = _('Enforcements')
    context['count'] = Enforcement.objects.count()
    enforcements = Enforcement.objects.all().order_by('policy')

    q = request.GET.get('q', None)
    if q != '':
        context['query'] = q
        condition = Q(policy__name__icontains=q) | Q(group__name__icontains=q)
        enforcements = Enforcement.objects.filter(condition)
    else:
        return redirect('/enforcements')

    context['enforcements'] = paginate(enforcements, request)
    return render(request, 'tncapp/enforcements.html', context)


def paginate(items, request):
    """
    Paginated browsing
    """
    paginator = Paginator(items, 50)  # Show 50 packages per page
    page = request.GET.get('page')
    try:
        enforcements = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        enforcements = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        enforcements = paginator.page(paginator.num_pages)

    return enforcements
