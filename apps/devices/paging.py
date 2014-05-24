# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from .models import Device, Product
from apps.front.paging import ProducerFactory


# PAGING PRODUCER

device_producer_factory = ProducerFactory(Device, 'description__icontains')

product_producer_factory = ProducerFactory(Product, 'name__icontains')


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
