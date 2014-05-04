# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json
from datetime import datetime

from django.template.loader import render_to_string
from dajaxice.decorators import dajaxice_register

from . import models
from . import paging as paging_functions
from apps.swid import models as swid_models


@dajaxice_register()
def sessions_for_device(request, device_id, date_from, date_to):
    dateobj_from, dateobj_to = map(datetime.utcfromtimestamp, [date_from, date_to])
    device = models.Device.objects.get(pk=device_id)
    sessions = device.sessions.filter(time__lte=dateobj_to, time__gte=dateobj_from)

    data = {'sessions': [
        {'id': s.id, 'time': s.time.strftime('%b %d %H:%M:%S %Y')}
        for s in sessions
    ]}

    return json.dumps(data)


@dajaxice_register()
def tags_for_session(request, session_id):
    session = models.Session.objects.get(pk=session_id)
    installed_tags = swid_models.Tag.get_installed_tags_with_time(session)
    tags = [
        {
            'name': tag.package_name,
            'version': tag.version,
            'unique-id': tag.unique_id,
            'installed': first_reported.strftime('%b %d %H:%M:%S %Y'),
        }
        for tag, first_reported in installed_tags
    ]
    data = {'swid-tag-count': len(tags), 'swid-tags': tags}
    return json.dumps(data)


@dajaxice_register()
def paging(request, template, list_producer, stat_producer, var_name, url_name,
           current_page, page_size, filter_query, pager_id):
    """
    Returns paged tables.

    Args:
        template (str):
            Name of the table template to be used, without .html extension.

        list_producer (str):
            Name of the key for the list producer function. The list producer is the function
            which creates the paged list.

        stat_producer (str);
            Name of the key for the stat producer function. The stat producer is the function
            which returns information about the page count.

        var_name (str):
            Name of the list variable used in the templated.

        current_page (int):
            Current page index, 0 based.

        page_size (int):
            Number of items to be shown on one page.

        filter_query (str):
            Query to filter the paged list/table.

    Returns:
        A json object:
        {
            current_page: <The current page index, 0 based>,
            page_count: <Number of pages (might change when filtered)>,
            html: <The rendered template (only provided if stats_only == False>
        }

    """
    # register list producer
    list_producer_dict = {
        'device_list': paging_functions.device_producer_factory.list(),
        'dir_list': paging_functions.directory_producer_factory.list(),
        'enforcement_list': paging_functions.enforcement_list_producer,
        'file_list': paging_functions.file_list_producer,
        'pkg_list': paging_functions.package_producer_factory.list(),
        'policy_list': paging_functions.policy_producer_factory.list(),
        'product_list': paging_functions.product_producer_factory.list(),
        'regid_list': paging_functions.regid_producer_factory.list(),
        'swid_list': paging_functions.swid_producer_factory.list(),
    }

    # register stat producer
    stat_producer_dict = {
        'device_stat': paging_functions.device_producer_factory.stat(),
        'dir_stat': paging_functions.directory_producer_factory.stat(),
        'enforcement_stat': paging_functions.enforcement_stat_producer,
        'file_stat': paging_functions.file_stat_producer,
        'pkg_stat': paging_functions.package_producer_factory.stat(),
        'policy_stat': paging_functions.policy_producer_factory.stat(),
        'product_stat': paging_functions.product_producer_factory.stat(),
        'regid_stat': paging_functions.regid_producer_factory.stat(),
        'swid_stat': paging_functions.swid_producer_factory.stat(),
    }

    # get page count from stat producer
    sp = stat_producer_dict.get(stat_producer)
    if sp is None:
        raise ValueError('Invalid stat producer: %s' % stat_producer)
    page_count = sp(page_size, filter_query)

    from_idx = current_page * page_size
    to_idx = from_idx + page_size

    # get element list form list producer
    lp = list_producer_dict.get(list_producer)
    if lp is None:
        raise ValueError('Invalid list producer: %s' % list_producer)
    element_list = lp(from_idx, to_idx, filter_query)

    template_context = {
        var_name: element_list,
        'current_page': current_page,
        'page_count': page_count,
        'filter_query': filter_query,
        'pager_id': pager_id,
        'url_name': url_name,
        'url_hash': paging_functions.get_url_hash(pager_id, current_page, filter_query),
    }

    # render the given template with the element list to a html string
    response = {
        'current_page': current_page,
        'page_count': page_count,
        'html': render_to_string(template + '.html', template_context)
    }

    return json.dumps(response)
