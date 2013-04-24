import re
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.http import (require_GET, require_POST,
        require_safe) # require_safe == GET or HEAD
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from models import (Group, Device, Product, Identity, Result, Measurement,
        Policy)

@require_GET
def index(request):
    answer='Select view:<br/><a href=./files>Files</a>'
    return HttpResponse(answer)

@require_GET
def login(request):
    return render(request, 'cygapp/login.html')

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
def group_delete(request, groupID):
    group = get_object_or_404(Group, pk=groupID)
    group.delete()

    messages.success(request, _('Group deleted!'))
    return redirect('/groups')


@require_GET
def devices(request):
    context = {}
    context['title'] = _('Devices')
    context['devices'] = Device.objects.all()
    return render(request, 'cygapp/devices.html', context)

@require_GET
def device(request, deviceID):
    try:
        device = Device.objects.get(pk=deviceID)
    except Device.DoesNotExist:
        device = None
        messages.error(request, _('Device not found!'))

    context = {}
    context['devices'] = Device.objects.all().order_by('description')
    context['title'] = _('Devices')

    if device:
        context['device'] = device
        members = device.groups.all().order_by('name')
        context['members'] = members
        context['products'] = Product.objects.all().order_by('name')

        groups = Group.objects.exclude(id__in = members.values_list('id',
            flat=True))
        context['groups'] = groups
        context['title'] = _('Device ') + device.description

    return render(request, 'cygapp/devices.html', context)

@require_GET
def device_add(request):
    context = {}
    context['title'] = _('New device')
    context['groups'] = Group.objects.all().order_by('name')
    context['products'] = Product.objects.all().order_by('name')
    context['devices'] = Device.objects.all()
    context['device'] = Device()
    return render(request, 'cygapp/devices.html', context)

@require_POST
def device_save(request):
    deviceID = request.POST['deviceId']
    if not (deviceID == 'None' or re.match(r'^\d+$', deviceID)):
        return HttpResponse(status=400)

    members = []
    if request.POST['memberlist'] != '':
        members = request.POST['memberlist'].split(',')

    for member in members:
        if not re.match(r'^\d+$', member):
            return HttpResponse(status=400)

    value = request.POST['value'].lower()
    if not re.match(r'^[a-f0-9]+$', value):
        return HttpResponse(status=400)

    description = request.POST['description']
    if not re.match(r'^[\S ]{0,50}$', description):
        return HttpResponse(status=400)
    
    productID = request.POST['product']
    if not re.match(r'^\d+$', productID):
        return HttpResponse(status=400)

    try:
        product = Product.objects.get(pk=productID)
    except Product.DoesNotExist:
        return HttpResponse(status=400)

    if deviceID == 'None':
        device = Device.objects.create(value=value, description=description,
                product=product)
    else:
        device = get_object_or_404(Device, pk=deviceID)
        device.value = value
        device.description = description
        device.product = product
        device.save()

    if members:
        device.groups.clear()
        members = Group.objects.filter(id__in=members)
        for member in members:
            device.groups.add(member)

        device.save()

    messages.success(request, _('Device saved!'))
    return redirect('/devices/%d' % device.id)


@require_GET
def device_delete(request, deviceID):
    device = get_object_or_404(Device, pk=deviceID)
    device.delete()

    messages.success(request, _('Device deleted!'))
    return redirect('/devices')


@require_GET
def products(request):
    context = {}
    context['title'] = _('Products')
    context['products'] = Product.objects.all().order_by('name')
    return render(request, 'cygapp/products.html', context)

@require_GET
def product(request, productID):
    try:
        product = Product.objects.get(pk=productID)
    except Product.DoesNotExist:
        product = None
        messages.error(request, _('Product not found!'))

    context = {}
    context['products'] = Product.objects.all().order_by('name')
    context['title'] = _('Products')

    if product:
        context['product'] = product
        defaults = product.default_groups.all().order_by('name')
        context['defaults'] = defaults

        groups = Group.objects.exclude(id__in = defaults.values_list('id',
            flat=True))
        context['groups'] = groups
        context['title'] = _('Product ') + product.name

    return render(request, 'cygapp/products.html', context)


@require_GET
def product_add(request):
    context = {}
    context['title'] = _('New product')
    context['groups'] = Group.objects.all().order_by('name')
    context['products'] = Product.objects.all().order_by('name')
    context['product'] = Product()
    return render(request, 'cygapp/products.html', context)


@require_POST
def product_save(request):
    productID = request.POST['productId']
    if not (productID == 'None' or re.match(r'^\d+$', productID)):
        return HttpResponse(status=400)

    defaults = []
    if request.POST['defaultlist'] != '':
        defaults = request.POST['defaultlist'].split(',')

    for default in defaults:
        if not re.match(r'^\d+$', default):
            return HttpResponse(status=400)

    name = request.POST['name']
    if not re.match(r'^[\S ]+$', name):
        return HttpResponse(status=400)

    if productID == 'None':
        product = Product.objects.create(name=name)
    else:
        product = get_object_or_404(Product, pk=productID)
        product.name = name
        product.save()

    if defaults:
        product.default_groups.clear()
        defaults = Group.objects.filter(id__in=defaults)
        for default in defaults:
            product.default_groups.add(default)

        product.save()

    messages.success(request, _('Product saved!'))
    return redirect('/products/%d' % product.id)

@require_GET
def product_delete(request, productID):
    product = get_object_or_404(Product, pk=productID)
    product.delete()

    messages.success(request, _('Product deleted!'))
    return redirect('/products')

@require_GET
def policies(request):
    context = {}
    context['title'] = _('Policies')
    context['policies'] = Policy.objects.all().order_by('name')
    return render(request, 'cygapp/policies.html', context)

@require_GET
def policy(request, policyID):
    try:
        policy = Policy.objects.get(pk=policyID)
    except Policy.DoesNotExist:
        policy = None
        messages.error(request, _('Policy not found!'))

    context = {}
    context['policies'] = Policy.objects.all().order_by('name')
    context['title'] = _('Policys')

    if policy:
        context['policy'] = policy
        enforcements = policy.enforcements.all().order_by('id')
        context['enforcements'] = enforcements
        context['types'] = Policy.types
        context['action'] = Policy.action

        groups = Group.objects.exclude(id__in = enforcements.values_list('id',
            flat=True))
        context['groups'] = groups
        context['title'] = _('Policy ') + policy.name

    return render(request, 'cygapp/policies.html', context)


@require_GET
def policy_add(request):
    pass

@require_POST
def policy_save(request):
    pass

@require_GET
def policy_delete(request):
    pass

@require_safe
def start_measurement(request):
    deviceID = request.GET.get('deviceID', '')
    if not re.match(r'^[a-f0-9]+$', deviceID):
        return HttpResponse(status=400)

    connectionID = request.GET.get('connectionID', '')
    if not re.match(r'^[0-9]+$', connectionID):
        return HttpResponse(status=400)

    arID = request.GET.get('arID', '')
    if not re.match(r'^\S+$', arID):
        return HttpResponse(status=400)

    OSVersion = request.GET['osVersion']
    product, new = Product.objects.get_or_create(name=OSVersion)

    if new:
        # TODO: Add entry for default group
        pass

    device, new = Device.objects.get_or_create(value=deviceID, product=product)

    if new:
        for group in device.product.default_groups.all():
            device.groups.add(group)

        device.save()

    id = Identity.objects.get_or_create(data=arID)[0]

    measurement = Measurement.objects.create(time=datetime.today(), identity=id,
            device=device, connectionID=connectionID)
    device.create_work_items(measurement)

    return HttpResponse(content=None)

#NOT a view, does not need a decorator
def generate_results(measurement):
    workitems = measurement.workitems.all()

    for item in workitems:
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
    deviceID = request.GET.get('deviceID', '')
    connectionID = request.GET.get('connectionID', '')

    try:
        measurement = Measurement.objects.get(device__value=deviceID,
                connectionID=connectionID) 
    except Measurement.DoesNotExist:
        return HttpResponse(status=404)

    generate_results(measurement)

    return HttpResponse(status=200)

