import re
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import (authenticate, login as django_login, logout as
        django_logout)
from django.views.decorators.http import (require_GET, require_safe,
        require_http_methods)
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from models import Session, Device, Product, Identity, Result, Action

@require_GET
def overview(request):
    return render(request, 'cygapp/overview.html')

@require_safe
def start_session(request):
    """
    Initializes a new session and creates workitems according to policy
    """

    purge_dead_sessions()

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

    session = Session.objects.create(time=datetime.today(), identity=id,
            device=device, connectionID=connectionID)
    device.create_work_items(session)

    return HttpResponse(content='')

@require_safe
def end_session(request):
    deviceID = request.GET.get('deviceID', '')
    connectionID = request.GET.get('connectionID', '')

    try:
        session = Session.objects.filter(device__value=deviceID,
                connectionID=connectionID).latest('time')
    except Session.DoesNotExist:
        return HttpResponse(status=404)

    generate_results(session)

    return HttpResponse(status=200)

@require_http_methods(('GET','POST'))
def login(request):
    if request.method == 'POST':
        password = request.POST.get('password', None)
        user = authenticate(username='cygnet-user', password=password)
        if user is not None and user.is_active:
                django_login(request, user)
                next = request.POST.get('next_url', None)
                if next is not None:
                    return redirect(next)
                else:
                    return redirect('/overview')
        else:
            messages.error(request, _('Bad password!'))

    if request.user.is_authenticated():
        return redirect('/overview')

    context = {'next_url': request.GET.get('next', '')}
    return render(request, 'cygapp/login.html', context)

def logout(request):
    django_logout(request)
    messages.success(request, _('Logout successful!'))

    return render(request, 'cygapp/login.html')
    

#NOT views, do not need decorators

def generate_results(session):
    workitems = session.workitems.all()

    for item in workitems:
        Result.objects.create(result=item.result, session=session,
                policy=item.enforcement.policy,
                recommendation=item.recommendation)

        if workitems:
            session.recommendation = max(workitems, key = lambda x:
                    x.recommendation)
    else:
        session.recommendation = Action.ALLOW

    for item in workitems:
        item.delete()


def purge_dead_sessions():
    MAX_AGE = 7 #days

    deadline = datetime.today() - timedelta(days=MAX_AGE)
    dead = Session.objects.filter(recommendation=None, time__lte=deadline)

    for d in dead:
        d.delete()
