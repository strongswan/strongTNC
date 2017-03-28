# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re

from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _

from .models import File, FileHash, Directory
from apps.policies.models import Policy, Enforcement


@require_GET
@login_required
def files(request):
    """
    All files
    """
    context = {}
    context['title'] = _('Files')
    return render(request, 'filesystem/files.html', context)


@require_GET
@login_required
def file(request, fileID):
    """
    File detail view
    """
    try:
        file = File.objects.get(pk=fileID)
    except File.DoesNotExist:
        file = None
        messages.error(request, _('File not found!'))

    context = {}
    context['title'] = _('Files')

    if file:
        context['file'] = file
        context['title'] = _('File ') + file.name
        file_hashes = file.filehash_set.all().order_by('version', 'algorithm')
        context['file_hashes'] = file_hashes

        policies = Policy.objects.filter(file=file)
        if file_hashes.count() or policies.count():
            context['has_dependencies'] = True
            context['policies'] = policies
            context['enforcements'] = Enforcement.objects.filter(policy__in=policies)

        swid_tags = file.tag_set.all()
        context['swid_tags'] = swid_tags

    return render(request, 'filesystem/files.html', context)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def save(request):
    """
    Insert view
    """
    name = request.POST.get('name', '')
    if not re.match(r'^[\S]+$', name):
        return HttpResponseBadRequest()

    dir_id = request.POST.get('dir')
    if dir_id is None or not re.match(r'^\d+$', dir_id):
        return HttpResponseBadRequest()

    try:
        new_file = File.objects.create(name=name, directory=Directory.objects.get(pk=dir_id))
    except Directory.DoesNotExist:
        return HttpResponseBadRequest()

    messages.success(request, _('File saved!'))
    return redirect('filesystem:file_detail', new_file.pk)


@require_GET
@login_required
@permission_required('auth.write_access', raise_exception=True)
def add(request):
    """
    Add a file
    """
    context = {}
    context['add'] = True
    context['title'] = _('New file')
    context['file'] = File()
    return render(request, 'filesystem/files.html', context)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def delete(request, fileID):
    """
    Delete a file
    """
    file = get_object_or_404(File, pk=fileID)
    file.delete()

    messages.success(request, _('File deleted!'))
    return redirect('filesystem:file_list')


@require_GET
@login_required
@permission_required('auth.write_access', raise_exception=True)
def delete_hash(request, file_hashID):
    """
    Delete a file hash
    """
    hash = get_object_or_404(FileHash, pk=file_hashID)
    file = hash.file
    hash.delete()

    messages.success(request, _('Hash deleted!'))
    return redirect('filesystem:file_detail', file.pk)
