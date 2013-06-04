import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from models import Group, Device

@require_GET
@login_required
def groups(request):
    context = {}
    context['groups'] = Group.objects.all().order_by('name')
    context['grouptree'] = group_tree()
    context['title'] = _('Groups')
    return render(request, 'cygapp/groups.html', context)

@require_GET
@login_required
def group(request, groupID):
    try:
        group = Group.objects.get(pk=groupID)
    except Group.DoesNotExist:
        group = None
        messages.msg_error(request, _('Group not found!'))

    context = {}
    context['groups'] = Group.objects.all().order_by('name')
    context['grouptree'] = group_tree()
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
@login_required
def add(request):
    context = {}
    context['title'] = _('New group')
    context['groups'] = Group.objects.all().order_by('name')
    context['grouptree'] = group_tree()
    context['group'] = Group()
    context['devices'] = Device.objects.all()
    return render(request, 'cygapp/groups.html', context)

@require_POST
@login_required
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

    group.members.clear()
    members = Device.objects.filter(id__in=members)
    for member in members:
        group.members.add(member)

    group.save()

    messages.success(request, _('Group saved!'))
    return redirect('/groups/%d' % group.id)

@require_POST
@login_required
def check(request):
    response = "false"
    if request.is_ajax():
        group_name = request.POST['name']
        group_id = request.POST['group']
        if group_id == 'None':
            group_id = ''
        group_id = int(group_id) if group_id != '' else -1
        
        g = Group.objects.filter(name=group_name).count()
        if g != 0:
            if group_id != '':
                group_byid = Group.objects.get(pk=group_id)
                if group_byid.name != group_name:
                    response = "false"
                else:
                    response = "true"
            else:
                response = "false"
        else:
            response = "true"

    return HttpResponse("%s" % response)

@require_POST
@login_required
def delete(request, groupID):
    group = get_object_or_404(Group, pk=groupID)

    if int(groupID) != 1:
        group.delete()
        messages.success(request, _('Group deleted!'))
    else:
        messages.error(request,
            _('Sorry, this is the default group and cannot be deleted'))

    return redirect('/groups')

def group_tree():
    """Returns a tree-view of all groups as <dl>-Tag."""

    dl = '<dl>\n'
    roots = Group.objects.filter(parent=None)

    for root in roots:
        #dl += '<dt>%s</dt>' % root
        dl += add_children(root)
        
    dl += '</dl>'

    return dl

def add_children(parent):
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


     
