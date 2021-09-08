# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re

from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _

from .models import Group, Device
from apps.policies.models import Enforcement


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
    return render(request, 'devices/groups.html', context)


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

        child_groups = group.get_children()
        parent_groups = group.get_parents()
        dependent_enforcements = Enforcement.objects.filter(Q(group=group) | Q(group__in=child_groups))
        applied_enforcements = Enforcement.objects.filter(Q(group=group) | Q(group__in=parent_groups))\
            .order_by('policy', 'group')
        context['applied_enforcements'] = applied_enforcements

        if len(child_groups) or dependent_enforcements.count():
            context['has_dependencies'] = True
            context['dependent_enforcements'] = dependent_enforcements
            context['child_groups'] = child_groups

    return render(request, 'devices/groups.html', context)


@require_GET
@login_required
@permission_required('auth.write_access', raise_exception=True)
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
    return render(request, 'devices/groups.html', context)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
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
    return redirect('devices:group_detail', group.pk)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def check(request):
    """
    Check if group name is unique

    Used for form validation with jQuery validator,
    http://jqueryvalidation.org/remote-method/

    Returns:
        - true for valid group name
        - false for invalid group name

    """
    is_valid = False
    if request.is_ajax():
        group_name = request.POST.get('name')
        group_id = request.POST.get('group')

        try:
            group_obj = Group.objects.get(name=group_name)
            is_valid = (str(group_obj.id) == group_id)
        except Group.DoesNotExist:
            is_valid = True

    return HttpResponse(("%s" % is_valid).lower())


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
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

    return redirect('devices:group_list')


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
    url = reverse('devices:group_detail', args=[parent.id])
    if parent.membergroups.all():
        sub += '<dd><dl>\n'
        sub += '<dt><a href="%s">%s</a></dt>\n' % (url, parent)
        for child in parent.membergroups.all():
            sub += add_children(child)
        sub += '</dl></dd>'
    else:
        sub += '<dd><a href="%s">%s</a></dd>\n' % (url, parent)

    return sub
