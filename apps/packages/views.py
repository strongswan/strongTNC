# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re

from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _

from .models import Package, Version


@require_GET
@login_required
def packages(request):
    """
    All packages
    """
    context = {}
    context['title'] = _('Packages')
    context['count'] = Package.objects.count()

    return render(request, 'packages/packages.html', context)


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

    if package:
        context['package'] = package
        versions = package.versions.all().order_by('release')
        context['versions'] = versions
        context['title'] = _('Package ') + package.name

    return render(request, 'packages/packages.html', context)


@require_GET
@login_required
@permission_required('auth.write_access', raise_exception=True)
def add(request):
    """
    Add a package
    """
    context = {}
    context['add'] = True
    context['title'] = _('New package')
    context['package'] = Package()
    return render(request, 'packages/packages.html', context)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def save(request):
    """
    Insert a package
    """
    package_id = request.POST['packageId']
    if not (package_id == 'None'):
        return HttpResponse(status=400)

    name = request.POST.get('name')
    if not re.match(r'^[\S]+$', name):
        return HttpResponse(status=400)

    package_entry = Package.objects.create(name=name)

    messages.success(request, _('Package saved!'))
    return redirect('packages:package_detail', package_entry.pk)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
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
@permission_required('auth.write_access', raise_exception=True)
def delete(request, packageID):
    """
    Delete a package
    """
    package = get_object_or_404(Package, pk=packageID)
    package.delete()

    messages.success(request, _('Package deleted!'))
    return redirect('packages:package_list')


@require_GET
@login_required
@permission_required('auth.write_access', raise_exception=True)
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
