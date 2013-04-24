import re
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_safe
from django.shortcuts import render
from models import Measurement, Device, Product, Identity, Result, Action

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

