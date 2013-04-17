from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.template import Context
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
import re
from models import *

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

# TODO: Add method decorators to check HTTP Methods

def index(request):
    answer='Select view:<br/><a href=./files>Files</a>'
    return HttpResponse(answer)

def overview(request):
    return render(request, 'cygapp/overview.html')

def groups(request):
    context = {}
    context['groups'] = Group.objects.all().order_by('name')
    context['title'] = _('Groups')
    return render(request, 'cygapp/groups.html', context)

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

def group_add(request):
    context = {}
    context['title'] = _('New group')
    context['groups'] = Group.objects.all().order_by('name')
    context['group'] = Group()
    context['devices'] = Device.objects.all()
    return render(request, 'cygapp/groups.html', context)

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

def group_delete(request, groupID):
    group = get_object_or_404(Group, pk=groupID)
    group.delete()

    messages.success(request, _('Group deleted!'))
    return redirect('/groups')


def fileshashes(request):
    flist = File.objects.all()
    answer = ''

    for f in flist:
        hashes = FileHash.objects.filter(file=f.id)
        answer += f.id.__str__() + ':' 
        answer += ','.join('%s' % h for h in hashes)

        answer += '\n'

    return HttpResponse(answer)

def fileshashesjson(request):
    flist = File.objects.all()
    answer = '{['

    for file in flist:
        hashes = FileHash.objects.filter(file=file.id)
        answer += ',\n'.join(hash.__json__() for hash in hashes)

    answer += ']}'
    return HttpResponse(answer, mimetype='application/json')

def fileedit(request, fileid):
    if request.method == 'GET':
        f = get_object_or_404(File, pk=fileid)
        dirs = Directory.objects.all()
        context = Context({ 'file': f,
                            'dirs': dirs})

        return render(request, 'cygapp/fileedit.html', context)

    elif request.method == 'POST':
        f = get_object_or_404(File, pk=fileid)
        f.name = request.POST['name']
        context = {}
        if request.POST['path'] is None or request.POST['path'] == '':
            context['file'] = f
            context['dirs'] = Directory.objects.all()
            context['message'] = 'Path cannot be empty!'
            return render(request, 'cygapp/fileedit.html', context)

        dir, created = Directory.objects.get_or_create( path = request.POST['path'] )
        if created:
            print('Warning: had to create new directory (' + str(dir.id) + ')')

        print(str(dir.id) + ': ' + dir.path)
        f.directory = dir
        f.save()
        return HttpResponseRedirect('/cygapp/files/' + str(f.id) + '/edit')
    
    #No valid HTTP method
    raise Http500


def filejson(request, fileid):
    f = get_object_or_404(File, pk=fileid)
    return HttpResponse(f.__json__(), mimetype='application/json')

def filehashes(request, fileid):
    f = get_object_or_404(File, pk=fileid)
    hashes = FileHash.objects.filter(file=f.id)
    if hashes.count() == 0:
        return HttpResponse('No hashes')
    
    return HttpResponse('<br/>\n'.join(hash.__str__() for hash in hashes))

def filehashesjson(request, fileid):
    f = get_object_or_404(File, pk=fileid)
    hashes = FileHash.objects.filter(file=f.id)
    if hashes.count() == 0:
        return HttpResponse('{}', mimetype='application/json')

    return HttpResponse('\n'.join(hash.__json__() for hash in hashes), mimetype='application/json')

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
    device.createWorkItems(measurement)

    return HttpResponse(content=None)

def generate_results(measurement):
    workitems = measurement.workitems.all()

    for item in workitems:
        #TODO: Result integrity check, see tannerli/cygnet-doc#34
        Result.objects.create(result=item.result, measurement=measurement,
                policy=item.enforcement.policy,
                recommendation=item.recommendation)

    measurement.recommendation = max(workitems, key = lambda x:
            x.recommendation)

    for item in workitems:
        item.delete()

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
