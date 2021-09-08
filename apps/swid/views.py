# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.views.generic import ListView, DetailView

from apps.core.models import Session, WorkItem
from apps.core.types import WorkItemType
from apps.authentication.mixins import LoginRequiredMixin
from apps.devices.models import Device
from .models import Entity, Tag
from . import utils


class RegidListView(LoginRequiredMixin, ListView):
    queryset = Entity.objects.order_by('regid')
    template_name = 'swid/regid_list.html'


class RegidDetailView(LoginRequiredMixin, DetailView):
    model = Entity
    template_name = 'swid/regid_detail.html'

    def get_context_data(self, **kwargs):
        context = super(RegidDetailView, self).get_context_data(**kwargs)
        context['paging_args'] = {'entity_id': self.object.pk}
        return context


class SwidTagListView(LoginRequiredMixin, ListView):
    model = Tag
    template_name = 'swid/tags_list.html'


class SwidTagDetailView(LoginRequiredMixin, DetailView):
    model = Tag
    template_name = 'swid/tags_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SwidTagDetailView, self).get_context_data(**kwargs)
        context['paging_args'] = {'tag_id': self.object.pk}
        context['entityroles'] = self.object.entityrole_set.all()
        return context


class SwidInventoryView(LoginRequiredMixin, DetailView):
    template_name = 'swid/swid_inventory.html'
    model = Device

    def get_context_data(self, **kwargs):
        context = super(SwidInventoryView, self).get_context_data(**kwargs)
        try:
            context['current_session'] = self.object.sessions.latest()
        except Session.DoesNotExist:
            context['current_session'] = None
        return context


class SwidLogView(LoginRequiredMixin, DetailView):
    template_name = 'swid/swid_log.html'
    model = Device

    def get_context_data(self, **kwargs):
        context = super(SwidLogView, self).get_context_data(**kwargs)
        return context


def import_swid_tags(session):
    workitem = WorkItem.objects.get(session=session, type=WorkItemType.SWIDT)
    result = workitem.result

    if not result:
        raise ValueError('No SWID tags provided')

    swid_tags = result.splitlines()

    for swid_tag in swid_tags:
        utils.process_swid_tag(swid_tag.encode('utf-8'))
