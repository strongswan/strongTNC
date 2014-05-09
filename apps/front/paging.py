# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import math

from django.db.models import Q

from apps.policies.models import Enforcement, Policy
from apps.devices.models import Device, Product
from apps.packages.models import Package
from apps.filesystem.models import File, Directory
from apps.swid.models import Tag, Entity


# TODO split up into apps


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
        def _func(from_idx, to_idx, filter_query):
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
        def _func(page_size, filter_query):
            qs = self.model.objects.all()
            if filter_query:
                kwargs = {self.filter_target: filter_query}
                qs = qs.filter(**kwargs)
            return math.ceil(qs.count() / page_size)
        return _func


# ************************* #
# DEVICE LIST/STAT PRODUCER #
# ************************* #
device_producer_factory = ProducerFactory(Device, 'description__icontains')


# **************************** #
# DIRECTORY LIST/STAT PRODUCER #
# **************************** #
directory_producer_factory = ProducerFactory(Directory, 'path__icontains')


# ****************************** #
# ENFORCEMENT LIST/STAT PRODUCER #
# ****************************** #
def enforcement_list_producer(from_idx, to_idx, filter_query):
    enforcement_list = Enforcement.objects.all()
    if filter_query:
        enforcement_list = Enforcement.objects.filter(
            Q(policy__name__icontains=filter_query) | Q(group__name__icontains=filter_query))
    return enforcement_list[from_idx:to_idx]


def enforcement_stat_producer(page_size, filter_query):
    count = Enforcement.objects.count()
    if filter_query:
        enforcement_list = Enforcement.objects.filter(
            Q(policy__name__icontains=filter_query) | Q(group__name__icontains=filter_query))
        count = enforcement_list.count()
    return math.ceil(count / page_size)


# *********************** #
# FILE LIST/STAT PRODUCER #
# *********************** #
def file_list_producer(from_idx, to_idx, filter_query):
    file_list = File.objects.all()
    if filter_query:
        file_list = File.filter(filter_query)
    return file_list[from_idx:to_idx]


def file_stat_producer(page_size, filter_query):
    count = File.objects.count()
    if filter_query:
        count = File.filter(filter_query).count()
    return math.ceil(count / page_size)


# ************************** #
# PACKAGE LIST/STAT PRODUCER #
# ************************** #
package_producer_factory = ProducerFactory(Package, 'name__icontains')


# ************************* #
# POLICY LIST/STAT PRODUCER #
# ************************* #
policy_producer_factory = ProducerFactory(Policy, 'name__icontains')


# ************************** #
# PRODUCT LIST/STAT PRODUCER #
# ************************** #
product_producer_factory = ProducerFactory(Product, 'name__icontains')


# ************************ #
# REGID LIST/STAT PRODUCER #
# ************************ #
regid_producer_factory = ProducerFactory(Entity, 'regid__icontains')


# ************************ #
# SWID LIST/STAT PRODUCER #
# ************************ #
swid_producer_factory = ProducerFactory(Tag, 'unique_id__icontains')


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
