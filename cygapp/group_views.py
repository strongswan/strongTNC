import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from models import Group, Device

@require_GET
def groups(request):
    context = {}
    context['groups'] = Group.objects.all().order_by('name')
    context['title'] = _('Groups')
    return render(request, 'cygapp/groups.html', context)

@require_GET
def group(request, groupID):
    try:
        group = Group.objects.get(pk=groupID)
    except Group.DoesNotExist:
        group = None
        messages.error(request, _('Group not found!'))

    context = {}
    context['groups'] = Group.objects.all().order_by('name')
    context['title'] = _('Groups')
    if group:
        context['group'] = group
        members = group.members.all()
        context['members'] = members

        devices = Device.objects.exclude(id__in = members.values_list('id',
            flat=True))

        context['devices'] = devices
        context['title'] = _('Group ') + context['group'].name

    return render(request, 'cygapp/groups.html', context)

@require_GET
def add(request):
    context = {}
    context['title'] = _('New group')
    context['groups'] = Group.objects.all().order_by('name')
    context['group'] = Group()
    context['devices'] = Device.objects.all()
    return render(request, 'cygapp/groups.html', context)

@require_POST
def save(request):
    groupID = request.POST['groupId']
    if not (groupID == 'None' or re.match(r'^\d+$', groupID)):
        return HttpResponse(status=400)

    members = []
    if request.POST['memberlist'] != '':
        members = request.POST['memberlist'].split(',')

    for member in members:
        if not re.match(r'^\d+$', member):
            return HttpResponse(status=400)

    name = request.POST['name']
    if not re.match(r'^[\S ]{1,50}$', name):
        return HttpResponse(status=400)

    parentId = request.POST['parent']
    if parentId == groupID:
        return HttpResponse(status=400)

    parent=None
    if parentId != '':
        try:
            parent=Group.objects.get(pk=parentId)
        except Group.DoesNotExist:
            pass

    if groupID == 'None':
        group = Group.objects.create(name=name,parent=parent)
    else:
        group = get_object_or_404(Group, pk=groupID)
        group.name = name
        group.parent = parent
        group.save()

    if members:
        group.members.clear()
        members = Device.objects.filter(id__in=members)
        for member in members:
            group.members.add(member)

        group.save()

    messages.success(request, _('Group saved!'))
    return redirect('/groups/%d' % group.id)


@require_GET
def delete(request, groupID):
    group = get_object_or_404(Group, pk=groupID)
    group.delete()

    messages.success(request, _('Group deleted!'))
    return redirect('/groups')


