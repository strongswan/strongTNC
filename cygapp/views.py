import re
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.http import (require_GET, require_POST,
        require_safe) # require_save == GET or HEAD
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from models import (Group, Device, Product, Identity, Result, Measurement,
        Action)

class Message(object):
    types = {
            'ok':'message_ok',
            'info':'message_info',
            'warning':'message_warning',
            'error':'message_error',
            }

    def __init__(self, type, text):
        self.text = text
        self.type = Message.types[type]

@require_GET
def index(request):
    answer='Select view:<br/><a href=./files>Files</a>'
    return HttpResponse(answer)

@require_GET
def overview(request):
    return render(request, 'cygapp/overview.html')

@require_GET
def groups(request):
    context = {}
    context['groups'] = Group.objects.all().order_by('name')
    context['title'] = _('Groups')
    return render(request, 'cygapp/groups.html', context)

@require_GET
def group(request, groupID):
    if request.method != 'GET':
        return HttpResponse(status=405)

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

        devices = Device.objects.all()
        devices = list(devices)
        for dev in devices:
            if dev in members:
                devices.remove(dev)

        context['devices'] = devices
        context['title'] = _('Group ') + context['group'].name

    return render(request, 'cygapp/groups.html', context)

@require_GET
def group_add(request):
    context = {}
    context['title'] = _('New group')
    context['groups'] = Group.objects.all().order_by('name')
    context['group'] = Group()
    context['devices'] = Device.objects.all()
    return render(request, 'cygapp/groups.html', context)

@require_POST
def group_save(request):
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

@require_POST
def group_delete(request, groupID):
    group = get_object_or_404(Group, pk=groupID)
    group.delete()

    messages.success(request, _('Group deleted!'))
    return redirect('/groups')


@require_safe
def start_measurement(request):
    #Sanitize input
    deviceID = request.GET.get('deviceID', '')
    if not re.match(r'^[a-f0-9]+$', deviceID):
        return HttpResponse(status=400)

    connectionID = request.GET.get('connectionID', '')
    if not re.match(r'^[0-9]+$', connectionID):
        return HttpResponse(status=400)

    ar_id = request.GET.get('ar_id', '')
    if not re.match(r'^\S+$', ar_id):
        return HttpResponse(status=400)

    OSVersion = request.GET['OSVersion']
    product, new = Product.objects.get_or_create(name=OSVersion)

    if new:
        # TODO: Add entry for default group
        pass

    device, new = Device.objects.get_or_create(value=deviceID, product=product)

    if new:
        for group in device.product.default_groups.all():
            device.groups.add(group)

        device.save()

    id = Identity.objects.get_or_create(data=ar_id)[0]

    measurement = Measurement.objects.create(time=datetime.today(), user=id,
            device=device, connectionID=connectionID)
    device.create_work_items(measurement)

    return HttpResponse(content=None)

@require_safe
def generate_results(measurement):
    workitems = measurement.workitems.all()

    for item in workitems:
        #TODO: Result integrity check, see tannerli/cygnet-doc#34
        Result.objects.create(result=item.result, measurement=measurement,
                policy=item.enforcement.policy,
                recommendation=item.recommendation)

        if workitems:
            measurement.recommendation = max(workitems, key = lambda x:
                    x.recommendation)
    else:
        measurement.recommendation = Action.ALLOW

    for item in workitems:
        item.delete()

@require_safe
def end_measurement(request):
    if request.method not in ('HEAD','GET'):
        return HttpResponse(status=405)

    deviceID = request.GET.get('deviceID', '')
    connectionID = request.GET.get('connectionID', '')

    try:
        measurement = Measurement.objects.get(device__value=deviceID,
                connectionID=connectionID) 
    except Measurement.DoesNotExist:
        return HttpResponse(404)

    generate_results(measurement)

    return HttpResponse(status=200)
