# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import math

from .models import Directory, File
from apps.front.paging import ProducerFactory

# PAGING PRODUCER

directory_producer_factory = ProducerFactory(Directory, 'path__icontains')


def file_list_producer(from_idx, to_idx, filter_query, dynamic_params=None, static_params=None):
    file_list = File.objects.all().order_by('directory', 'name')
    if filter_query:
        file_list = File.filter(filter_query, order_by=('directory', 'name'))
    return file_list[from_idx:to_idx]


def file_stat_producer(page_size, filter_query, dynamic_params=None, static_params=None):
    count = File.objects.count()
    if filter_query:
        files = File.filter(filter_query)
        try:
            count = files.count()
        except TypeError:  # `files` is a list object
            count = len(files)
    return math.ceil(count / page_size)


def file_simple_list_producer(from_idx, to_idx, filter_query, dynamic_params=None, static_params=None):
    if not dynamic_params:
        return []
    directory_id = dynamic_params['directory_id']
    file_list = File.objects.filter(directory__id=int(directory_id))
    if filter_query:
        file_list = file_list.filter(name__icontains=filter_query)
    return file_list[from_idx:to_idx]


def file_simple_stat_producer(page_size, filter_query, dynamic_params=None, static_params=None):
    if not dynamic_params:
        return []
    directory_id = dynamic_params['directory_id']
    file_list = File.objects.filter(directory__id=directory_id)
    count = file_list.filter(directory__id=directory_id).count()
    if filter_query:
        count = file_list.filter(name__icontains=filter_query).count()
    return math.ceil(count / page_size)


# PAGING CONFIG

dir_list_paging = {
    'template_name': 'front/paging/default_list',
    'list_producer': directory_producer_factory.list(),
    'stat_producer': directory_producer_factory.stat(),
    'static_producer_args': None,
    'var_name': 'object_list',
    'url_name': 'filesystem:directory_detail',
    'page_size': 50,
}

dir_file_list_paging = {
    'template_name': 'filesystem/paging/simple_file_list',
    'list_producer': file_simple_list_producer,
    'stat_producer': file_simple_stat_producer,
    'url_name': 'filesystem:file_detail',
    'page_size': 45,
}

file_list_paging = {
    'template_name': 'front/paging/default_list',
    'list_producer': file_list_producer,
    'stat_producer': file_stat_producer,
    'static_producer_args': None,
    'var_name': 'object_list',
    'url_name': 'filesystem:file_detail',
    'page_size': 50,
}
