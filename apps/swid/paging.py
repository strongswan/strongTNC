# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import math

from .models import Entity, Tag
from apps.front.paging import ProducerFactory

# PAGING PRODUCER

swid_producer_factory = ProducerFactory(Tag, 'unique_id__icontains')

regid_producer_factory = ProducerFactory(Entity, 'regid__icontains')


def entity_swid_list_producer(from_idx, to_idx, filter_query, dynamic_params=None, static_params=None):
    entity_id = dynamic_params['entity_id']
    tag_list = Entity.objects.get(pk=entity_id).tags.all()
    if filter_query:
        tag_list = tag_list.filter(unique_id__icontains=filter_query)
    return tag_list[from_idx:to_idx]


def entity_swid_stat_producer(page_size, filter_query, dynamic_params=None, static_params=None):
    entity_id = dynamic_params['entity_id']
    tag_list = Entity.objects.get(pk=entity_id).tags.all()
    count = tag_list.count()
    if filter_query:
        count = tag_list.filter(unique_id__icontains=filter_query).count()
    return math.ceil(count / page_size)


# PAGING CONFIGS

regid_list_paging = {
    'template_name': 'front/paging/default_list',
    'list_producer': regid_producer_factory.list(),
    'stat_producer': regid_producer_factory.stat(),
    'static_producer_args': None,
    'var_name': 'object_list',
    'url_name': 'swid:regid_detail',
    'page_size': 50,
}

regid_detail_paging = {
    'template_name': 'front/paging/regid_list_tags',
    'list_producer': entity_swid_list_producer,
    'stat_producer': entity_swid_stat_producer,
    'static_producer_args': None,
    'var_name': 'object_list',
    'url_name': 'swid:tag_detail',
    'page_size': 50,
}

swid_list_paging = {
    'template_name': 'front/paging/default_list',
    'list_producer': swid_producer_factory.list(),
    'stat_producer': swid_producer_factory.stat(),
    'static_producer_args': None,
    'var_name': 'object_list',
    'url_name': 'swid:tag_detail',
    'page_size': 50,
}
