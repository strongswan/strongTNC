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
Provides CRUD for packages
"""

import re
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import Package, Version


@require_GET
@login_required
def packages(request):
    """
    All packages
    """
    context = {}
    context['title'] = _('Packages')
    context['count'] = Package.objects.count()
    packages = Package.objects.all().order_by('name')

    context['packages'] = paginate(packages, request)
    return render(request, 'tncapp/packages.html', context)


@require_GET
@login_required
def package(request, packageID):
    """
    Package detail view
    """
    try:
        package = Package.objects.get(pk=packageID)
    except Package.DoesNotExist:
        package = None
        messages.error(request, _('Package not found!'))

    context = {}
    context['title'] = _('Packages')
    context['count'] = Package.objects.count()
    packages = Package.objects.all().order_by('name')
    context['packages'] = paginate(packages, request)

    if package:
        context['package'] = package
        versions = package.versions.all().order_by('release')
        context['versions'] = versions
        context['title'] = _('Package ') + package.name

    return render(request, 'tncapp/packages.html', context)


@require_GET
@login_required
def add(request):
    """
    Add a package
    """
    context = {}
    context['title'] = _('New package')
    context['count'] = Package.objects.count()
    packages = Package.objects.all().order_by('name')
    context['packages'] = paginate(packages, request)
    context['package'] = Package()
    return render(request, 'tncapp/packages.html', context)


@require_POST
@login_required
def save(request):
    """
    Insert/update a package
    """
    packageID = request.POST['packageId']
    if not (packageID == 'None' or re.match(r'^\d+$', packageID)):
        return HttpResponse(status=400)

    name = request.POST['name']
    if not re.match(r'^[\S]+$', name):
        return HttpResponse(status=400)

    if packageID == 'None':
        package = Package.objects.create(name=name)
    else:
        package = get_object_or_404(Package, pk=packageID)
        package.name = name
        package.save()

    messages.success(request, _('Package saved!'))
    return redirect('/packages/%d' % package.id)


@require_POST
@login_required
def check(request):
    """
    Check if package name is unique
    """
    response = False
    if request.is_ajax():
        package_name = request.POST['name']
        package_id = request.POST['package']
        if package_id == 'None':
            package_id = ''

        try:
            package = Package.objects.get(name=package_name)
            response = (str(package.id) == package_id)
        except Package.DoesNotExist:
            response = True

    return HttpResponse(("%s" % response).lower())


@require_POST
@login_required
def delete(request, packageID):
    """
    Delete a package
    """
    package = get_object_or_404(Package, pk=packageID)
    package.delete()

    messages.success(request, _('Package deleted!'))
    return redirect('/packages')


@require_GET
@login_required
def toggle_version(request, versionID):
    """
    Toggle the blacklist state of a package version
    """
    version = get_object_or_404(Version, pk=versionID)
    if version.blacklist is None:
        version.blacklist = 1 if version.package.blacklist == 0 else 0
    else:
        version.blacklist = 1 if version.blacklist == 0 else 0

    version.save()
    return HttpResponse(_('Yes' if version.blacklist else 'No'))


@require_GET
@login_required
def search(request):
    """
    Filter packages
    """
    context = {}
    context['title'] = _('Packages')
    context['count'] = Package.objects.count()
    packages = Package.objects.all().order_by('name')

    q = request.GET.get('q', None)
    if q != '':
        context['query'] = q
        packages = Package.objects.filter(name__icontains=q)
    else:
        return redirect('/packages')

    context['packages'] = paginate(packages, request)
    return render(request, 'tncapp/packages.html', context)


def paginate(items, request):
    """
    Paginated browsing
    """
    paginator = Paginator(items, 50)  # Show 50 packages per page
    page = request.GET.get('page')
    try:
        packages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        packages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        packages = paginator.page(paginator.num_pages)

    return packages

