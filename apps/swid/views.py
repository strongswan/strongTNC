# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.views.generic import ListView, DetailView

from apps.core.models import WorkItem
from apps.core.types import WorkItemType
from apps.auth.mixins import LoginRequiredMixin
from apps.devices.models import Device
from .models import Entity, Tag
from . import utils as swid_utils


class RegidListView(LoginRequiredMixin, ListView):
    queryset = Entity.objects.order_by('regid')
    template_name = 'swid/regid_list.html'


class RegidDetailView(LoginRequiredMixin, DetailView):
    model = Entity
    template_name = 'swid/regid_detail.html'

    def get_context_data(self, **kwargs):
        context = super(RegidDetailView, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.order_by('regid')
        return context


class SwidTagListView(LoginRequiredMixin, ListView):
    queryset = Tag.objects.order_by('unique_id')
    template_name = 'swid/tags_list.html'


class SwidTagDetailView(LoginRequiredMixin, DetailView):
    model = Tag
    template_name = 'swid/tags_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SwidTagDetailView, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.order_by('unique_id')
        context['entityroles'] = self.object.entityrole_set.all()
        return context


class SwidInventoryView(DetailView):
    template_name = 'swid/swid_inventory.html'
    model = Device

    def get_context_data(self, **kwargs):
        context = super(SwidInventoryView, self).get_context_data(**kwargs)
        context['current_session'] = self.object.sessions.latest()
        return context


def import_swid_tags(session):
    workitem = WorkItem.objects.get(session=session, type=WorkItemType.SWIDT)
    result = workitem.result

    if not result:
        raise ValueError('No SWID tags provided')

    swid_tags = result.splitlines()

    for swid_tag in swid_tags:
        swid_utils.process_swid_tag(swid_tag.encode('utf-8'))
