# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re
import json

from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.http import HttpResponseBadRequest

from .models import Package, Version
from apps.swid.models import Tag
from apps.devices.models import Product
from apps.front.utils import checkbox_boolean, check_not_empty


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

    if package:
        context['package'] = package
        versions = package.versions.all().order_by('release')
        context['versions'] = versions
        context['title'] = _('Package ') + package.name
        if versions.count():
            context['has_dependencies'] = True

        swid_tags = Tag.objects.filter(package_name=package.name)
        context['swid_tags'] = swid_tags

    context['products'] = Product.objects.all()
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

    # update package information (e.g blacklist and security flags)
    if not (package_id == 'None'):
        data = request.POST['version-data']
        objects = json.loads(data)
        for version_flags in objects:
            version = Version.objects.get(pk=version_flags['id'])
            version.security = version_flags['security']
            version.blacklist = version_flags['blacklist']
            version.save()

        messages.success(request, _('Package updated!'))
        return redirect('packages:package_detail', package_id)

    # create new package
    else:
        name = request.POST.get('name')
        if not re.match(r'^[\S]+$', name):
            return HttpResponseBadRequest()

        package_entry = Package.objects.create(name=name)

        messages.success(request, _('Package saved!'))
        return redirect('packages:package_detail', package_entry.pk)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def check(request):
    """
    Check if package name is unique

    Used for form validation with jQuery validator,
    http://jqueryvalidation.org/remote-method/

    Returns:
    - true for valid package name
    - false for invalid package name
    """
    is_valid = False
    if request.is_ajax():
        package_name = request.POST.get('name')
        package_id = request.POST.get('package')
        if package_id == 'None':
            package_id = ''

        try:
            package_obj = Package.objects.get(name=package_name)
            is_valid = (str(package_obj.id) == package_id)
        except Package.DoesNotExist:
            is_valid = True

    return HttpResponse(("%s" % is_valid).lower())


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def delete(request, packageID):
    """
    Delete a package
    """
    package_obj = get_object_or_404(Package, pk=packageID)
    package_obj.delete()

    messages.success(request, _('Package deleted!'))
    return redirect('packages:package_list')


@require_GET
@login_required
@permission_required('auth.write_access', raise_exception=True)
def delete_version(request, packageID, versionID):
    """
    Delete a version
    """
    version = get_object_or_404(Version, pk=versionID)
    release = version.release
    version.delete()
    messages.success(request, _('Version %s deleted' % release))

    return redirect('packages:package_detail', packageID)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def add_version(request, packageID):
    """
    Add a new version
    """
    try:
        version = check_not_empty(request.POST.get('version'))
        product_id = check_not_empty(request.POST.get('product'))
        package = Package.objects.get(pk=packageID)
        product = Product.objects.get(pk=product_id)
    except (ValueError, Package.DoesNotExist, Product.DoesNotExist):
        return HttpResponseBadRequest()

    blacklist = checkbox_boolean(request.POST.get('blacklist'))
    security = checkbox_boolean(request.POST.get('security'))

    now = timezone.now()
    Version.objects.create(package=package, product=product, release=version, security=security,
                           blacklist=blacklist, time=now)

    messages.success(request, _('Version created!'))

    return redirect('packages:package_detail', package.pk)
