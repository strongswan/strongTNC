#
# Copyright (C) 2013 Marco Tanner
# Copyright (C) 2013 Stefan Rohner
# HSR University of Applied Sciences Rapperswil
#
# This file is part of strongTNC.  strongTNC is free software: you can
# redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# strongTNC is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with strongTNC.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Provides CRUD for products
"""

import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import Product, Group

@require_GET
@login_required
def products(request):
    """
    All products
    """
    context = {}
    context['title'] = _('Products')
    context['count'] = Product.objects.count()
    products = Product.objects.all().order_by('name')

    context['products'] = paginate(products, request)
    return render(request, 'tncapp/products.html', context)

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
    context['count'] = Product.objects.count()
    products = Product.objects.all().order_by('name')

    context['products'] = paginate(products, request)

    if product:
        context['product'] = product
        defaults = product.default_groups.all().order_by('name')
        context['defaults'] = defaults
        groups = Group.objects.exclude(id__in = defaults.values_list('id',
            flat=True))
        context['groups'] = groups
        context['title'] = _('Product ') + product.name

    return render(request, 'tncapp/products.html', context)


@require_GET
@login_required
def add(request):
    """
    Add new Product
    """
    context = {}
    context['title'] = _('New product')
    context['count'] = Product.objects.count()
    context['groups'] = Group.objects.all().order_by('name')
    products = Product.objects.all().order_by('name')
    context['products'] = paginate(products, request)
    context['product'] = Product()
    return render(request, 'tncapp/products.html', context)


@require_POST
@login_required
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
def delete(request, productID):
    """
    Delete a product
    """
    product = get_object_or_404(Product, pk=productID)
    product.delete()

    messages.success(request, _('Product deleted!'))
    return redirect('/products')

@require_GET
@login_required
def search(request):
    """
    Filter products
    """
    context = {}
    context['title'] = _('Product')
    context['count'] = Product.objects.count()
    products = Product.objects.all().order_by('name')

    q = request.GET.get('q', None)
    if q != '':
        context['query'] = q
        products = Product.objects.filter(name__icontains=q)
    else:
        return redirect('/products')

    context['products'] = paginate(products, request)
    return render(request, 'tncapp/products.html', context)

def paginate(items, request):
    """
    Paginated browsing
    """
    paginator = Paginator(items, 50) # Show 50 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    return products
