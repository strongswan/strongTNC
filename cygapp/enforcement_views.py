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
        context['title'] = _('Enforcement ') + str(enforcement)
        context['policies'] = Policy.objects.all().order_by('name')

    return render(request, 'cygapp/enforcements.html', context)


@require_GET
def add(request):
    context = {}
    context['title'] = _('New enforcement')
    context['groups'] = Group.objects.all().order_by('name')
    context['policies'] = Policy.objects.all().order_by('name')
    context['enforcement'] = Enforcement()
    return render(request, 'cygapp/enforcements.html', context)


@require_POST
def save(request):
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
def delete(request, enforcementID):
    enforcement = get_object_or_404(Enforcement, pk=enforcementID)
    enforcement.delete()

    return HttpResponse(status=200)

