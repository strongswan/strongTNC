# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re

from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from .models import ComponentHash


@require_GET
@login_required
def comphash(request, comp_hashID):
    """
    ComponentHash detail view
    """
    hash = get_object_or_404(ComponentHash, pk=comp_hashID)
    device = hash.device

    context = {}
    context['comphash'] = hash
    context['device'] = device
    context['title'] = _('Component Hash ') + str(hash.component) + \
        str(hash.seq_no) + ' (PCR ' + str(hash.pcr) + ') for ' + str(device)

    return render(request, 'tpm/comp_hashes.html', context)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def save(request):
    """
    Update a component hash
    """
    comp_hashID = request.POST['hashId']
    if not (comp_hashID == 'None' or re.match(r'^\d+$', comp_hashID)):
        return HttpResponseBadRequest()

    comp_hash = get_object_or_404(ComponentHash, pk=comp_hashID)
    hash = request.POST['hash'].lower()
    if not re.match(r'^[a-f0-9]+$', hash):
        messages.error(request, _("Component hash has incorrect hex format!"))
    else:
        comp_hash.hash = hash
        comp_hash.save()
        messages.success(request, _('Component hash saved!'))

    return redirect('tpm:comphash_detail', comp_hash.pk)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def delete(request, comp_hashID):
    """
    Delete a component hash
    """
    hash = get_object_or_404(ComponentHash, pk=comp_hashID)
    device = hash.device
    hash.delete()

    messages.success(request, _('Component hash deleted!'))
    return redirect('tpm:tpm_evidence', device.pk)
