# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.views.generic import ListView, DetailView

from apps.auth.mixins import LoginRequiredMixin
from . import models


class RegidListView(LoginRequiredMixin, ListView):
    queryset = models.Entity.objects.order_by('regid')
    template_name = 'swid/regid_list.html'


class RegidDetailView(LoginRequiredMixin, DetailView):
    model = models.Entity
    template_name = 'swid/regid_detail.html'

    def get_context_data(self, **kwargs):
        context = super(RegidDetailView, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.order_by('regid')
        return context


class SwidTagListView(LoginRequiredMixin, ListView):
    queryset = models.Tag.objects.order_by('unique_id')
    template_name = 'swid/tags_list.html'


class SwidTagDetailView(LoginRequiredMixin, DetailView):
    model = models.Tag
    template_name = 'swid/tags_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SwidTagDetailView, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.order_by('unique_id')
        context['entityroles'] = self.object.entityrole_set.all()
        return context
