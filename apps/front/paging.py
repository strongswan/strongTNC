# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import math


# **************** #
# PRODUCER FACTORY #
# **************** #
class ProducerFactory(object):
    """
    Class that generates list and stat producer functions.

    Example usage::

        device_producer_factory = ProducerFactory(Device, 'description__icontains')
        device_list_producer = device_producer_factory.list()
        device_stat_producer = device_producer_factory.stat()

    """
    def __init__(self, model, filter_target):
        """
        Initialize a new producer.

        Args:
            model:
                The model class that you want to quer.
            query_filter:
                The target for the filter query, for example
                ``description__icontains``.

        """
        self.model = model
        self.filter_target = filter_target

    def list(self):
        """
        Return a list producer function.
        """
        def _func(from_idx, to_idx, filter_query, *args):
            qs = self.model.objects.all()
            if filter_query:
                kwargs = {self.filter_target: filter_query}
                qs = qs.filter(**kwargs)
            return qs[from_idx:to_idx]
        return _func

    def stat(self):
        """
        Return a list producer function.
        """
        def _func(page_size, filter_query, *args):
            qs = self.model.objects.all()
            if filter_query:
                kwargs = {self.filter_target: filter_query}
                qs = qs.filter(**kwargs)
            return math.ceil(qs.count() / page_size)
        return _func


# ************* #
# PAGING HELPER #
# ************* #
def get_url_hash(pager_id, current_page, filter_query):
    page_param = 'page'
    filter_param = 'filter'

    if pager_id != 0:
        page_param = '%s%i' % (page_param, pager_id)
        filter_param = '%s%i' % (filter_param, pager_id)

    url_hash = '#%s=%i' % (page_param, current_page)
    if filter_query:
        url_hash += '&%s=%s' % (filter_param, filter_query)

    return url_hash
