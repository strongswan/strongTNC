# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re

from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _

from .models import Product, Group


@require_GET
@login_required
def products(request):
    """
    All products
    """
    context = {}
    context['title'] = _('Products')
    return render(request, 'devices/products.html', context)


@require_GET
@login_required
def product(request, productID):
    """
    Product detail view
    """
    try:
        product = Product.objects.get(pk=productID)
    except Product.DoesNotExist:
        product = None
        messages.error(request, _('Product not found!'))

    context = {}
    context['title'] = _('Products')

    if product:
        context['product'] = product
        defaults = product.default_groups.all().order_by('name')
        context['defaults'] = defaults
        groups = Group.objects.exclude(id__in=defaults.values_list('id', flat=True))
        context['groups'] = groups
        context['title'] = _('Product ') + product.name

    return render(request, 'devices/products.html', context)


@require_GET
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def add(request):
    """
    Add new Product
    """
    context = {}
    context['title'] = _('New product')
    context['groups'] = Group.objects.all().order_by('name')
    context['product'] = Product()
    return render(request, 'devices/products.html', context)


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def save(request):
    """
    Insert/update a product
    """
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


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def check(request):
    """
    Check if product name is unique
    """
    response = False
    if request.is_ajax():
        product_name = request.POST['name']
        product_id = request.POST['product']
        if product_id == 'None':
            product_id = ''

        try:
            product = Product.objects.get(name=product_name)
            response = (str(product.id) == product_id)
        except Product.DoesNotExist:
            response = True

    return HttpResponse(("%s" % response).lower())


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def delete(request, productID):
    """
    Delete a product
    """
    product = get_object_or_404(Product, pk=productID)
    product.delete()

    messages.success(request, _('Product deleted!'))
    return redirect('/products')
