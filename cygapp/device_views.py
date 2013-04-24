import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from models import Device, Group, Product

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
def add(request):
    context = {}
    context['title'] = _('New device')
    context['groups'] = Group.objects.all().order_by('name')
    context['products'] = Product.objects.all().order_by('name')
    context['devices'] = Device.objects.all()
    context['device'] = Device()
    return render(request, 'cygapp/devices.html', context)

@require_POST
def save(request):
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
def delete(request, deviceID):
    device = get_object_or_404(Device, pk=deviceID)
    device.delete()

    messages.success(request, _('Device deleted!'))
    return redirect('/devices')


