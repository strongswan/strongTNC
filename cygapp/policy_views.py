import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from models import Policy, Group

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
def add(request):
    context = {}
    context['policies'] = Policy.objects.all().order_by('name')
    context['title'] = _('New policy')
    context['types'] = Policy.types
    context['action'] = Policy.action
    context['policy'] = Policy()
    return render(request, 'cygapp/policies.html', context)

@require_POST
def save(request):
    policyID = request.POST['policyId']
    if not (policyID == 'None' or re.match(r'^\d+$', policyID)):
        raise ValueError
        return HttpResponse(status=400)

    type = request.POST['type']
    if not re.match(r'^\d+$', type) and int(type) in range(len(Policy.types)):
        raise ValueError
        return HttpResponse(status=400)

    fail = request.POST['fail']
    if not re.match(r'^\d+$', fail) and int(fail) in range(len(Policy.action)):
        raise ValueError
        return HttpResponse(status=400)

    noresult = request.POST['noresult']
    if not (re.match(r'^\d+$', noresult) and int(noresult) in
            range(len(Policy.action))):
        raise ValueError
        return HttpResponse(status=400)

    name = request.POST['name']
    if not re.match(r'^[\S ]+$', name):
        raise ValueError
        return HttpResponse(status=400)

    if policyID == 'None':
        policy = Policy.objects.create(name=name, type=type, fail=fail,
                noresult=noresult)
    else:
        policy = get_object_or_404(Policy, pk=policyID)
        policy.name = name
        policy.save()

    messages.success(request, _('Policy saved!'))
    return redirect('/policies/%d' % policy.id)


@require_GET
def delete(request, policyID):
    policy = get_object_or_404(Policy, pk=policyID)
    policy.delete()

    messages.success(request, _('Policy deleted!'))
    return redirect('/policies')

