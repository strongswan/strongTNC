import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from models import Product, Group, Enforcement, Policy

@require_GET
def enforcements(request):
    context = {}
    context['enforcements'] = Enforcement.objects.all().order_by('policy')
    context['title'] = _('Enforcements')
    
    return render(request, 'cygapp/enforcements.html', context)

@require_GET
def enforcement(request, enforcementID):
    try:
        enforcement = Enforcement.objects.get(pk=enforcementID)
    except Enforcement.DoesNotExist:
        enforcement = None
        messages.error(request, _('Enforcement not found!'))

    context = {}
    context['enforcements'] = Enforcement.objects.all().order_by('policy')
    context['title'] = _('Enforcements')

    if enforcement:
        context['enforcement'] = enforcement
        groups = Group.objects.all().order_by('name')
        context['groups'] = groups
        context['actions'] = Policy.action
        context['title'] = _('Enforcement ') + str(enforcement)
        context['policies'] = Policy.objects.all().order_by('name')

    return render(request, 'cygapp/enforcements.html', context)


@require_GET
def add(request):
    context = {}
    context['title'] = _('New enforcement')
    context['groups'] = Group.objects.all().order_by('name')
    context['policies'] = Policy.objects.all().order_by('name')
    context['enforcements'] = Enforcement.objects.all().order_by('policy')
    enforcement = Enforcement()
    enforcement.max_age = 0
    context['enforcement'] = enforcement
    context['actions'] = Policy.action
    return render(request, 'cygapp/enforcements.html', context)


@require_POST
def save(request):
    enforcementID = request.POST['enforcementId']
    if not (enforcementID == 'None' or re.match(r'^\d+$', enforcementID)):
        return HttpResponse(status=400)

    max_age = request.POST['max_age']
    if not re.match(r'^\d+$', max_age):
        return HttpResponse(status=400)

    policyID = request.POST['policy']
    if not re.match(r'^\d+$', policyID):
        return HttpResponse(status=400)

    groupID = request.POST['group']
    if not re.match(r'^\d+$', groupID):
        return HttpResponse(status=400)

    try:
        policy = Policy.objects.get(pk=policyID)
        group = Group.objects.get(pk=groupID)
    except (Policy.DoesNotExist, Group.DoesNotExist):
        return HttpResponse(status=400)
        
    fail = request.POST['fail']
    if not re.match(r'^[0123]$', fail):
        return HttpResponse(status=400)

    noresult = request.POST['noresult']
    if not re.match(r'^[0123]$', noresult):
        return HttpResponse(status=400)


    if enforcementID == 'None':
        enforcement = Enforcement.objects.create(group=group, policy=policy,
                max_age=max_age, fail=fail, noresult=noresult)
    else:
        enforcement = get_object_or_404(Product, pk=enforcementID)
        assert False
        enforcement.group = group
        enforcement.policy = policy
        enforcement.max_age = max_age
        enforcement.fail = fail
        enforcement.noresult = noresult
        enforcement.save()

    messages.success(request, _('Enforcement saved!'))
    return redirect('/enforcements/%d' % enforcement.id)

@require_GET
def delete(request, enforcementID):
    enforcement = get_object_or_404(Enforcement, pk=enforcementID)
    enforcement.delete()

    return HttpResponse(status=200)

