import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from models import Group, Enforcement, Policy

@require_GET
@login_required
def enforcements(request):
    context = {}
    context['enforcements'] = Enforcement.objects.all().order_by('policy')
    context['title'] = _('Enforcements')
    
    return render(request, 'cygapp/enforcements.html', context)

@require_GET
@login_required
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
@login_required
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
@login_required
def save(request):
    enforcementID = request.POST['enforcementId']
    if not (enforcementID == 'None' or re.match(r'^\d+$', enforcementID)):
        raise ValueError
        return HttpResponse(status=400)

    max_age = request.POST['max_age']
    if not re.match(r'^\d+$', max_age):
        raise ValueError
        return HttpResponse(status=400)

    policyID = request.POST['policy']
    if not re.match(r'^\d+$', policyID):
        raise ValueError
        return HttpResponse(status=400)

    groupID = request.POST['group']
    if not re.match(r'^\d+$', groupID):
        raise ValueError
        return HttpResponse(status=400)

    try:
        policy = Policy.objects.get(pk=policyID)
        group = Group.objects.get(pk=groupID)
    except (Policy.DoesNotExist, Group.DoesNotExist):
        raise ValueError
        return HttpResponse(status=400)

    fail = request.POST.get('fail', None)
    if not (re.match(r'^-?\d+$', fail) and int(fail) in range(-1,
        len(Policy.action))):
        raise ValueError
        return HttpResponse(status=400)

    fail = int(fail)
    if fail == -1:
        fail = None

    noresult = request.POST.get('noresult', -1)
    if not (re.match(r'^-?\d+$', noresult) and int(noresult) in range(-1,
        len(Policy.action))):
        raise ValueError
        return HttpResponse(status=400)

    noresult = int(noresult)
    if noresult == -1:
        noresult = None

    if enforcementID == 'None':
        enforcement = Enforcement.objects.create(group=group, policy=policy,
                max_age=max_age, fail=fail, noresult=noresult)
    else:
        enforcement = get_object_or_404(Enforcement, pk=enforcementID)
        enforcement.group = group
        enforcement.policy = policy
        enforcement.max_age = max_age
        enforcement.fail = fail
        enforcement.noresult = noresult
        enforcement.save()

    messages.success(request, _('Enforcement saved!'))
    return redirect('/enforcements/%d' % enforcement.id)

@require_POST
@login_required
def check(request):
    response = "false"
    if request.is_ajax():
        policy_id = request.POST['policy']
        policy_id = int(policy_id) if policy_id != '' else -1
        group_id = request.POST['group']
        group_id = int(group_id) if group_id != '' else -1
        enforcement_id = request.POST['enforcement']
        enforcement_id = int(enforcement_id) if enforcement_id != '' else -1

        try:
            e = Enforcement.objects.get(policy=policy_id, group=group_id)

            if e.id == enforcement_id:
                response = "true"
        except Enforcement.DoesNotExist:
            response =  "true"

    return HttpResponse("%s" % response)

@require_POST
@login_required
def delete(request, enforcementID):
    enforcement = get_object_or_404(Enforcement, pk=enforcementID)
    enforcement.delete()

    messages.success(request, _('Enforcement deleted!'))
    return redirect('/enforcements')

