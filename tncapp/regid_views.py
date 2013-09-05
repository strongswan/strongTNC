#
# Copyright (C) 2013 Andreas Steffen
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
Provides CRUD for regids
"""

import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from models import Regid, Tag

@require_GET
@login_required
def regids(request):
    """
    All regids
    """
    context = {}
    context['title'] = _('Regids')
    context['count'] = Regid.objects.count()
    regids = Regid.objects.all().order_by('name')
    context['regids'] = paginate(regids, request)
    return render(request, 'tncapp/regids.html', context)

@require_GET
@login_required
def regid(request,regidID):
    """
    Regid detail view
    """
    try:
        regid = Regid.objects.get(pk=regidID)
    except Regid.DoesNotExist:
        regid = None
        messages.error(request, _('Regid not found!'))

    context = {}
    context['title'] = _('Regids')
    context['count'] = Regid.objects.count()
    regids = Regid.objects.all().order_by('name')

    context['regids'] = paginate(regids, request)

    if regids:
        context['regid'] = regid
        context['title'] = _('Regid ') + regid.name
        tags = Tag.objects.filter(regid=regid).order_by('unique_sw_id')
        context['tags'] = tags

    return render(request, 'tncapp/regids.html', context)

@require_GET
@login_required
def add(request):
    """
    Add a regid
    """
    context = {}
    context['title'] = _('New regid')
    context['count'] = Regid.objects.count()
    regids = Regid.objects.all().order_by('name')
    context['regids'] = paginate(regids, request)
    context['regid'] = Regid()
    return render(request, 'tncapp/regids.html', context)

@require_POST
@login_required
def save(request):
    """
    Insert/update view
    """
    regidID = request.POST['regidId']
    if not (regidID == 'None' or re.match(r'^\d+$', regidID)):
        return HttpResponse(status=400)

    name = request.POST['name']
    if not re.match(r'^[\S]+$', name):
        return HttpResponse(status=400)

    if regidID == 'None':
        regid = Regid.objects.create(name=name)
    else:
        regid = get_object_or_404(Regid, pk=regidID)
        regid.name = name
        regid.save()

    messages.success(request, _('Regid saved!'))
    return redirect('/regids/%d' % regid.id)

@require_POST
@login_required
def delete(request, regidID):
    """
    Delete a regid
    """
    regid = get_object_or_404(Regid, pk=regidID)
    regid.delete()

    messages.success(request, _('Regid deleted!'))
    return redirect('/regids')

@require_GET
@login_required
def search(request):
    """
    Filter regids
    """
    context = {}
    context['title'] = _('Regids')
    context['count'] = Regid.objects.count()
    regids = Regid.objects.all().order_by('name')

    q = request.GET.get('q', None)
    if q != '':
        context['query'] = q
        q1 = Q(name__icontains=q)
        regids = Regid.objects.filter(q1)
    else:
        return redirect('/regids')

    context['regids'] = paginate(regids, request)
    return render(request, 'tncapp/regids.html', context)

def paginate(items, request):
    """
    Paginated browsing
    """
    paginator = Paginator(items, 50) # Show 50 packages per page
    page = request.GET.get('page')
    try:
        regids = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        regids = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        regids = paginator.page(paginator.num_pages)

    return regids

