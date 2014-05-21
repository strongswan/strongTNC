# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import math

from .models import Device, Product
from apps.core.models import Session
from apps.front.paging import ProducerFactory


# PAGING PRODUCER

device_producer_factory = ProducerFactory(Device, 'description__icontains')

product_producer_factory = ProducerFactory(Product, 'name__icontains')


def device_session_list_producer(from_idx, to_idx, filter_query, dynamic_params=None, static_params=None):
    device_id = dynamic_params['device_id']
    session_list = Session.objects.filter(device=device_id)
    return session_list[from_idx:to_idx]


def device_session_stat_producer(page_size, filter_query, dynamic_params=None, static_params=None):
    device_id = dynamic_params['device_id']
    count = Session.objects.filter(device=device_id).count()
    return math.ceil(count / page_size)


# PAGING CONFIGS

device_list_paging = {
    'template_name': 'front/paging/default_list',
    'list_producer': device_producer_factory.list(),
    'stat_producer': device_producer_factory.stat(),
    'static_producer_args': None,
    'var_name': 'object_list',
    'url_name': 'devices:device_detail',
    'page_size': 50,
}

product_list_paging = {
    'template_name': 'front/paging/default_list',
    'list_producer': product_producer_factory.list(),
    'stat_producer': product_producer_factory.stat(),
    'static_producer_args': None,
    'var_name': 'object_list',
    'url_name': 'devices:product_detail',
    'page_size': 50,
}

device_session_list_paging = {
    'template_name': 'devices/paging/device_report_sessions',
    'list_producer': device_session_list_producer,
    'stat_producer': device_session_stat_producer,
    'static_producer_args': None,
    'var_name': 'sessions',
    'url_name': 'devices:session_detail',
    'page_size': 30,
}
