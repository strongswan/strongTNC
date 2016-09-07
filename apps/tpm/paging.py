# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import math
from collections import OrderedDict, namedtuple

from django.core.urlresolvers import reverse

from apps.devices.models import Device
from apps.front.utils import timestamp_local_to_utc
from apps.front.paging import ProducerFactory

# PAGING PRODUCER

tpm_device_producer_factory = ProducerFactory(Device, 'description__icontains')


# PAGING CONFIGS

tpm_devices_list_paging = {
    'template_name': 'front/paging/default_list',
    'list_producer': tpm_device_producer_factory.list(),
    'stat_producer': tpm_device_producer_factory.stat(),
    'static_producer_args': None,
    'var_name': 'object_list',
    'url_name': 'tpm:tpm_evidence',
    'page_size': 50,
}
