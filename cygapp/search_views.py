"""
Defines backend-views for site-wide search
"""

from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from models import Group, Policy, Enforcement, Device, Package, Product, File

@require_GET
@login_required
def search(request):
    """
    Global search view
    """
    context = {}
    context['group_title'] = _('Groups')
    context['policy_title'] = _('Policies')
    context['enforcement_title'] = _('Enforcements')
    context['device_title'] = _('Devices')
    context['package_title'] = _('Packages')
    context['product_title'] = _('Products')
    context['file_title'] = _('Files')
    
    context['groups'] = Group.objects.all().order_by('name')
    context['policies'] = Policy.objects.all().order_by('name')
    context['enforcements'] = Enforcement.objects.all().order_by('policy')
    context['devices'] = Device.objects.all().order_by('description')
    context['packages'] = Package.objects.all().order_by('name')
    context['products'] = Product.objects.all().order_by('name')
    context['files'] = File.objects.all().order_by('name')
    
    q = request.GET.get('q', '')
    if q != '':
        context['query'] = q
        context['groups'] = Group.objects.filter(name__icontains=q)
        context['policies'] = Policy.objects.filter(name__icontains=q)
        context['enforcements'] = Enforcement.objects.filter(Q(policy__name__icontains=q)|Q(group__name__icontains=q))
        context['devices'] = Device.objects.filter(Q(description__icontains=q)|Q(value__icontains=q))
        context['packages'] = Package.objects.filter(name__icontains=q)
        context['products'] = Product.objects.filter(name__icontains=q)
        q1 = Q(name__icontains=q)
        q2 = Q(directory__path__icontains=q)
        context['files'] = File.objects.filter(q1 | q2)

    return render(request, 'cygapp/search.html', context)
