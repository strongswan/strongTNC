# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from .models import Package
from apps.front.paging import ProducerFactory


# PAGING PRODUCER

package_producer_factory = ProducerFactory(Package, 'name__icontains')

# PAGING CONFIGS

package_list_paging = {
    'template_name': 'front/paging/default_list',
    'list_producer': package_producer_factory.list(),
    'stat_producer': package_producer_factory.stat(),
    'static_producer_args': None,
    'var_name': 'object_list',
    'url_name': 'packages:package_detail',
    'page_size': 50,
}
