# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _

from apps.devices.models import Device
from .models import ComponentHash


@require_GET
@login_required
def evidence(request, deviceID):
    """
    Generate TPM evicence for given device
    """
    device = get_object_or_404(Device, pk=deviceID)

    context = {}
    context['device'] = device
    context['title'] = _('TPM Evidence for ') + str(device)
    context['paging_args'] = {'device_id': device.pk}
    comp_hashes = ComponentHash.objects.filter(device=device).order_by('seq_no')
    context['comp_hashes'] = comp_hashes
    context['comp_hashes_count'] = comp_hashes.count()

    return render(request, 'tpm/tpm_evidence.html', context)


@require_POST
@login_required
@permission_required('auth.write_access', raise_exception=True)
def comphashes_delete(request, deviceID):
    """
    Delete all component hashes
    """
    device = get_object_or_404(Device, pk=deviceID)
    comp_hashes = ComponentHash.objects.filter(device=device).order_by('seq_no')
    comp_hashes.delete()

    messages.success(request, _('All composite hashes deleted!'))
    return redirect('tpm:tpm_evidence', device.pk)
