from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.shortcuts import render
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
    pass

@require_POST
def save(request):
    pass

@require_GET
def delete(request):
    pass

