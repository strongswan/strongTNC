from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
import re
from models import *

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
    context = {}
    context['groups'] = Group.objects.all().order_by('name')
    context['group'] = Group.objects.get(pk=groupID)
    context['title'] = _('Group ') + context['group'].name
    return render(request, 'cygapp/groups.html', context)

def group_add(request):
    context = {}
    context['title'] = _('New group')
    context['groups'] = Group.objects.all().order_by('name')
    context['group'] = Group()
    return render(request, 'cygapp/groups.html', context)

def group_save(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    groupID = request.POST['groupId']

    if groupID == 'None':
        group = Group.objects.create(name=request.POST['name'],
                parent=Group.objects.get(pk=request.POST['parent']))
    else:
        group = get_object_or_404(Group, pk=groupID)
        group.name = request.POST['name']
        group.parent = Group.objects.get(pk=request.POST['parent'])
        group.save()

    return redirect('/groups/%d' % group.id)

def group_delete(request, groupID):
    group = get_object_or_404(Group, pk=groupID)
    group.delete()

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
    deviceID = request.GET.get('deviceID', '')
    connectionID = request.GET.get('connectionID', '')

    try:
        measurement = Measurement.objects.get(device__value=deviceID,
                connectionID=connectionID) 
    except Measurement.DoesNotExist:
        return HttpResponse(404)

    generate_results(measurement)
    
    return HttpResponse(status=200)
