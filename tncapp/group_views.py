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
Provides CRUD for groups
"""

import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from models import Group, Device


@require_GET
@login_required
def groups(request):
    """
    All groups
    """
    context = {}
    context['groups'] = Group.objects.all().order_by('name')
    context['grouptree'] = group_tree()
    context['title'] = _('Groups')
    return render(request, 'tncapp/groups.html', context)


@require_GET
@login_required
def group(request, groupID):
    """
    Group detail view
    """
    try:
        group = Group.objects.get(pk=groupID)
    except Group.DoesNotExist:
        group = None
        messages.error(request, _('Group not found!'))

    context = {}
    context['groups'] = Group.objects.all().order_by('name')
    context['grouptree'] = group_tree()
    context['title'] = _('Groups')
    if group:
        context['group'] = group
        group_members = group.devices.all()
        context['group_members'] = group_members

        devices = Device.objects.exclude(id__in=group_members.values_list('id', flat=True))

        context['devices'] = devices
        context['title'] = _('Group ') + context['group'].name

    return render(request, 'tncapp/groups.html', context)


@require_GET
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def add(request):
    """
    Add new group
    """
    context = {}
    context['title'] = _('New group')
    context['groups'] = Group.objects.all().order_by('name')
    context['grouptree'] = group_tree()
    context['group'] = Group()
    context['devices'] = Device.objects.all()
    return render(request, 'tncapp/groups.html', context)


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def save(request):
    """
    Insert/update a group
    """
    groupID = request.POST['groupId']
    if not (groupID == 'None' or re.match(r'^\d+$', groupID)):
        return HttpResponse(status=400)

    group_members = []
    if request.POST['memberlist'] != '':
        group_members = request.POST['memberlist'].split(',')

    for device in group_members:
        if not re.match(r'^\d+$', device):
            return HttpResponse(status=400)

    name = request.POST['name']
    if not re.match(r'^[\S ]{1,50}$', name):
        return HttpResponse(status=400)

    parentId = request.POST['parent']
    if parentId == groupID:
        return HttpResponse(status=400)

    parent = None
    if parentId != '':
        try:
            parent = Group.objects.get(pk=parentId)
        except Group.DoesNotExist:
            pass

    if groupID == 'None':
        group = Group.objects.create(name=name, parent=parent)
    else:
        group = get_object_or_404(Group, pk=groupID)
        group.name = name
        group.parent = parent
        group.save()

    group.devices.clear()
    devices = Device.objects.filter(id__in=group_members)
    for device in devices:
        group.devices.add(device)

    group.save()

    messages.success(request, _('Group saved!'))
    return redirect('/groups/%d' % group.id)


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def check(request):
    """
    Check if group name is unique
    """
    response = False
    if request.is_ajax():
        group_name = request.POST['name']
        group_id = request.POST['group']
        if group_id == 'None':
            group_id = ''

        try:
            group = Group.objects.get(name=group_name)
            response = (str(group.id) == group_id)
        except Group.DoesNotExist:
            response = True

    return HttpResponse(("%s" % response).lower())


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def delete(request, groupID):
    """
    Delete a group
    """
    group = get_object_or_404(Group, pk=groupID)

    if int(groupID) != 1:
        group.delete()
        messages.success(request, _('Group deleted!'))
    else:
        messages.error(request,
            _('Sorry, this is the default group and cannot be deleted'))

    return redirect('/groups')


def group_tree():
    """
    Returns a tree-view of all groups as <dl>-Tag.
    """

    dl = '<dl>\n'
    roots = Group.objects.filter(parent=None)

    for root in roots:
        dl += add_children(root)

    dl += '</dl>'

    return dl


def add_children(parent):
    """
    Recursion method for group_tree()
    """
    sub = ''
    if parent.membergroups.all():
        sub += '<dd><dl>\n'
        sub += '<dt><a href="/groups/%d">%s</a></dt>\n' % (parent.id, parent)
        for child in parent.membergroups.all():
            sub += add_children(child)
        sub += '</dl></dd>'
    else:
        sub += '<dd><a href="/groups/%d">%s</a></dd>\n' % (parent.id, parent)

    return sub
