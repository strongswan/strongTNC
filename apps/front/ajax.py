# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json

from django.template.loader import render_to_string

from django.http import HttpResponse
from django.views.decorators.http import require_POST

from apps.core.decorators import ajax_login_required
from . import paging as paging_functions
from apps.swid.paging import regid_detail_paging, regid_list_paging, swid_list_paging
from apps.swid.paging import swid_inventory_list_paging, swid_log_list_paging
from apps.swid.paging import swid_inventory_session_paging
from apps.swid.paging import swid_files_list_paging, swid_devices_list_paging
from apps.filesystem.paging import dir_list_paging, file_list_paging, dir_file_list_paging
from apps.policies.paging import policy_list_paging, enforcement_list_paging
from apps.packages.paging import package_list_paging
from apps.devices.paging import device_list_paging, product_list_paging, device_session_list_paging
from apps.devices.paging import product_devices_list_paging, device_event_list_paging
from apps.devices.paging import device_vulnerability_list_paging
from apps.tpm.paging import tpm_devices_list_paging


@require_POST
@ajax_login_required
def paging(request):
    """
    Returns paged tables.

    Args:
        config_name (str):
            Name of the paging config to be used. This name is the key in of the config
            dictionary.
            The config holds values such as the list/stat-producer, template_name,
            var_name, url_name, page_size and so on.

        current_page (int):
            Current page index, 0 based.

        filter_query (str):
            Query to filter the paged list/table.

        pager_id (int):
            Id of the current pager, used to identify the pager in the url via hash-query.

        producer_args (dict):
            Dictionary with dynamic custom arguments which are passed to the producers.

    Returns:
        A json object:
        {
            current_page: <The current page index, 0 based>,
            page_count: <Number of pages (might change when filtered)>,
            html: <The rendered template (only provided if stats_only == False>
        }

    """
    config_name = request.POST.get('config_name')
    current_page = int(request.POST.get('current_page'))
    filter_query = request.POST.get('filter_query')
    pager_id = int(request.POST.get('pager_id'))
    producer_args = json.loads(request.POST.get('producer_args'))
    # TODO: extract this to somewhere else
    # register configs
    paging_conf_dict = {
        'regid_list_config': regid_list_paging,
        'regid_detail_config': regid_detail_paging,
        'swid_list_config': swid_list_paging,
        'dir_list_config': dir_list_paging,
        'file_list_config': file_list_paging,
        'policy_list_config': policy_list_paging,
        'enforcement_list_config': enforcement_list_paging,
        'package_list_config': package_list_paging,
        'device_list_config': device_list_paging,
        'product_list_config': product_list_paging,
        'device_session_list_config': device_session_list_paging,
        'device_event_list_config': device_event_list_paging,
        'device_vulnerability_list_config': device_vulnerability_list_paging,
        'swid_inventory_list_config': swid_inventory_list_paging,
        'swid_log_list_config': swid_log_list_paging,
        'swid_inventory_session_list_config': swid_inventory_session_paging,
        'dir_file_list_config': dir_file_list_paging,
        'swid_files_list_config': swid_files_list_paging,
        'product_devices_list_config': product_devices_list_paging,
        'swid_devices_list_config': swid_devices_list_paging,
        'tpm_devices_list_config': tpm_devices_list_paging,
    }

    conf = paging_conf_dict[config_name]
    page_size = conf.get('page_size', 50)

    # get page count from stat producer
    sp = conf.get('stat_producer')
    if sp is None:
        raise ValueError('Invalid stat producer')
    page_count = sp(page_size, filter_query, producer_args, conf.get('static_producer_args'))

    from_idx = current_page * page_size
    to_idx = from_idx + page_size

    # get element list form list producer
    lp = conf.get('list_producer')
    if lp is None:
        raise ValueError('Invalid list producer')
    element_list = lp(from_idx, to_idx, filter_query, producer_args, conf.get('static_producer_args'))

    var_name = conf.get('var_name', 'object_list')
    template_context = {
        var_name: element_list,
        'current_page': current_page,
        'page_count': page_count,
        'filter_query': filter_query,
        'pager_id': pager_id,
        'url_name': conf.get('url_name'),
        'url_hash': paging_functions.get_url_hash(pager_id, current_page, filter_query),
    }

    # render the given template with the element list to a html string
    template_name = conf.get('template_name', 'front/paging/default_list')
    response = {
        'current_page': current_page,
        'page_count': page_count,
        'html': render_to_string(template_name + '.html', template_context)
    }
    return HttpResponse(json.dumps(response), content_type="application/x-json")
