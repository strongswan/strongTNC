# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.views.generic import ListView, DetailView

from apps.core.models import Session
from apps.auth.mixins import LoginRequiredMixin
from apps.devices.models import Device
from .models import Entity, Tag


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
        context['devices'] = self.object.get_devices_with_reported_session()
        return context


class SwidInventoryView(DetailView):
    template_name = 'swid/swid_inventory.html'
    model = Device

    def get_context_data(self, **kwargs):
        context = super(SwidInventoryView, self).get_context_data(**kwargs)
        try:
            context['current_session'] = self.object.sessions.latest()
        except Session.DoesNotExist:
            context['current_session'] = None
        return context
