# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re

from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _

from .models import Directory, File


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

    if directories:
        context['directory'] = directory
        context['title'] = _('Directory ') + directory.path
        files = File.objects.filter(directory=directory).order_by('name')
        context['files'] = files

    return render(request, 'filesystem/directories.html', context)


@require_GET
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def add(request):
    """
    Add a directory
    """
    context = {}
    context['title'] = _('New directory')
    context['directory'] = Directory()
    return render(request, 'filesystem/directories.html', context)


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def save(request):
    """
    Insert/update view
    """
    directoryID = request.POST['directoryId']
    if not (directoryID == 'None' or re.match(r'^\d+$', directoryID)):
        return HttpResponse(status=400)

    path = request.POST['path']
    if not re.match(r'^[\S]+$', path):
        return HttpResponse(status=400)

    if directoryID == 'None':
        directory = Directory.objects.create(path=path)
    else:
        directory = get_object_or_404(Directory, pk=directoryID)
        directory.path = path
        directory.save()

    messages.success(request, _('Directory saved!'))
    return redirect('/directories/%d' % directory.id)


@require_POST
@login_required
@permission_required('tncapp.write_access', raise_exception=True)
def delete(request, directoryID):
    """
    Delete a directory
    """
    directory = get_object_or_404(Directory, pk=directoryID)
    directory.delete()

    messages.success(request, _('Directory deleted!'))
    return redirect('/directories')
