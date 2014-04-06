#
# Copyright (C) 2013 Marco Tanner
# Copyright (C) 2013 Stefan Rohner
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
Provides CRUD for tags
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
from models import Tag


@require_GET
@login_required
def tags(request):
    """
    All tags
    """
    context = {}
    context['title'] = _('Tags')
    context['count'] = Tag.objects.count()
    tags = Tag.objects.all().order_by('regid__name', 'unique_sw_id')
    context['tags'] = paginate(tags, request)
    return render(request, 'tncapp/tags.html', context)


@require_GET
@login_required
def tag(request, tagID):
    """
    Tag detail view
    """
    try:
        tag = Tag.objects.get(pk=tagID)
    except Tag.DoesNotExist:
        tag = None
        messages.error(request, _('Tag not found!'))

    context = {}
    context['title'] = _('Tags')
    context['count'] = Tag.objects.count()
    tags = Tag.objects.all().order_by('regid__name', 'unique_sw_id')

    context['tags'] = paginate(tags, request)

    if tag:
        context['tag'] = tag
        context['title'] = _('Tag ') + tag.unique_sw_id

    return render(request, 'tncapp/tags.html', context)


@require_POST
@login_required
def save(request):
    """
    Insert/update view
    """
    tagID = request.POST['tagId']
    if not (tagID == 'None' or re.match(r'^\d+$', tagID)):
        return HttpResponse(status=400)

    unique_sw_id = request.POST['unique_sw_id']
    if not re.match(r'^[\S]+$', unique_sw_id):
        return HttpResponse(status=400)

    messages.success(request, _('Tag saved!'))
    return redirect('/tags/%d' % tag.id)


@require_POST
@login_required
def delete(request, tagID):
    """
    Delete a tag
    """
    tag = get_object_or_404(Tag, pk=tagID)
    tag.delete()

    messages.success(request, _('Tag deleted!'))
    return redirect('/tags')


@require_GET
@login_required
def search(request):
    """
    Filter tags
    """
    context = {}
    context['title'] = _('Tags')
    context['count'] = Tag.objects.count()
    tags = Tag.objects.all().order_by('unique_sw_id')

    q = request.GET.get('q', None)
    if q != '':
        context['query'] = q
        q1 = Q(unique_sw_id__icontains=q)
        q2 = Q(regid__name__icontains=q)
        tags = Tag.objects.filter(q1 | q2)
    else:
        return redirect('/tags')

    context['tags'] = paginate(tags, request)
    return render(request, 'tncapp/tags.html', context)


def paginate(items, request):
    """
    Paginated browsing
    """
    paginator = Paginator(items, 50)  # Show 50 packages per page
    page = request.GET.get('page')
    try:
        tags = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tags = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        tags = paginator.page(paginator.num_pages)

    return tags
