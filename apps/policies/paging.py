# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import math

from django.db.models import Q

from .models import Policy, Enforcement
from apps.front.paging import ProducerFactory


# PAGING PRODUCER

policy_producer_factory = ProducerFactory(Policy, 'name__icontains')


def enforcement_list_producer(from_idx, to_idx, filter_query, dynamic_params=None, static_params=None):
    enforcement_list = Enforcement.objects.all()
    if filter_query:
        enforcement_list = Enforcement.objects.filter(
            Q(policy__name__icontains=filter_query) | Q(group__name__icontains=filter_query))
    return enforcement_list[from_idx:to_idx]


def enforcement_stat_producer(page_size, filter_query, dynamic_params=None, static_params=None):
    count = Enforcement.objects.count()
    if filter_query:
        enforcement_list = Enforcement.objects.filter(
            Q(policy__name__icontains=filter_query) | Q(group__name__icontains=filter_query))
        count = enforcement_list.count()
    return math.ceil(count / page_size)


# PAGING CONFIGS

policy_list_paging = {
    'template_name': 'front/paging/default_list',
    'list_producer': policy_producer_factory.list(),
    'stat_producer': policy_producer_factory.stat(),
    'static_producer_args': None,
    'var_name': 'object_list',
    'url_name': 'policies:policy_detail',
    'page_size': 50,
}

enforcement_list_paging = {
    'template_name': 'front/paging/default_list',
    'list_producer': enforcement_list_producer,
    'stat_producer': enforcement_stat_producer,
    'static_producer_args': None,
    'var_name': 'object_list',
    'url_name': 'policies:enforcement_detail',
    'page_size': 50,
}
