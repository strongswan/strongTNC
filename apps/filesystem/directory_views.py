# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re

from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from .models import Directory, File
from apps.policies.models import Policy, Enforcement


@require_GET
@login_required
def directories(request):
    """
    All directories
    """
    context = {}
    context['title'] = _('Directories')
    return render(request, 'filesystem/directories.html', context)


@require_GET
@login_required
def directory(request, directoryID):
    """
    Directory detail view
    """
    try:
        directory = Directory.objects.get(pk=directoryID)
    except Directory.DoesNotExist:
        directory = None
        messages.error(request, _('Directory not found!'))

    context = {}
    context['title'] = _('Directories')

    if directory:
        context['directory'] = directory
        context['title'] = _('Directory ') + directory.path
        files = File.objects.filter(directory=directory).order_by('name')
        context['files'] = files
        context['paging_params'] = {'directory_id': directory.pk}
        policies = Policy.objects.filter(Q(dir=directory) | Q(file__in=files))
        if policies.count() or files.count():
            context['has_dependencies'] = True
            context['policies'] = policies
            context['enforcements'] = Enforcement.objects.filter(policy__in=policies)

    return render(request, 'filesystem/directories.html', context)


@require_GET
@login_required
@permission_required('auth.write_access', raise_exception=True)
def add(request):
    """
    Add a directory
    """
    context = {}
    context['add'] = True
    context['title'] = _('New directory')
    context['directory'] = Directory()
    return render(request, 'filesystem/directories.html', context)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def save(request):
    """
    Insert view
    """
    directory_id = request.POST['directoryId']
    if not directory_id == 'None':
        return HttpResponse(status=400)

    path = request.POST['path']
    if not re.match(r'^[\S]+$', path):
        return HttpResponse(status=400)

    directory_entry = Directory.objects.create(path=path)

    messages.success(request, _('Directory created!'))
    return redirect('filesystem:directory_detail', directory_entry.pk)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def delete(request, directoryID):
    """
    Delete a directory
    """
    directory = get_object_or_404(Directory, pk=directoryID)
    directory.delete()

    messages.success(request, _('Directory deleted!'))
    return redirect('filesystem:directory_list')


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def check(request):
    """
    Check if directory name is unique

    Used for form validation with jQuery validator,
    http://jqueryvalidation.org/remote-method/

    Returns:
        - true for valid directory name
        - false for invalid directory name

    """
    is_valid = False
    if request.is_ajax():
        directory_path = request.POST.get('path')
        directory_id = request.POST.get('directory')

        try:
            dir_obj = Directory.objects.get(path=directory_path)
            is_valid = (str(dir_obj.id) == directory_id)
        except Directory.DoesNotExist:
            is_valid = True

    return HttpResponse(("%s" % is_valid).lower())
