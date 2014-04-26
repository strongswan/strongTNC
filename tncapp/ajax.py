# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json
import os.path
from datetime import datetime

from django.template.loader import render_to_string

from dajaxice.decorators import dajaxice_register

from tncapp import models
from apps.swid.model_queries import get_installed_tags_with_time


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
    tags = []
    for tag, first_reported in get_installed_tags_with_time(session_id):
        tags.append({
            'name': tag.package_name,
            'version': tag.version,
            'unique-id': tag.unique_id,
            'installed': first_reported.strftime('%b %d %H:%M:%S %Y')
        })

    data = {'swid-tag-count': len(tags), 'swid-tags': tags}
    return json.dumps(data)


@dajaxice_register()
def files_autocomplete(request, search_term):
    """
    Provides the autocomplete backend for the file dropdown in the policy view.

    Args:
        request (request):
            The django request object.

        search_term (str):
            The search term, should be a filename or path or a combination.

    Returns:
        A json object in the following form, eg.:
            {
                result: [
                    {id: 758, 'text': '/bin/bash'},
                    {id: 65, 'text': '/bin/netcat'}
                ]
            }


    This ajax function, especially the result format is made to work with
    the autocomplete feature of the jQuery plugin Select2: http://ivaynberg.github.io/select2/

    """
    path_part, file_part = os.path.split(search_term)

    files = dirs = None

    # collecting the data from two tables
    if file_part and not path_part:
        files = models.File.objects.filter(name__icontains=file_part)
        dirs = models.Directory.objects.filter(path__icontains=file_part)

    if path_part and not file_part:
        dirs = models.Directory.objects.filter(path__icontains=path_part)

    if path_part and file_part:
        files = models.File.objects.filter(name__icontains=file_part)
        dirs = models.Directory.objects.filter(path__icontains=search_term)

    resulting_files = []

    # prepare results from collected data
    if files and not dirs:
        resulting_files = files

    if dirs and not files:
        resulting_files = models.File.objects.filter(directory__in=dirs)

    if dirs and files:
        resulting_files = files | models.File.objects.filter(directory__in=dirs)

    # create resulting json to return
    options = [{'id': f.id, 'file': '/'.join([f.directory.path.rstrip('/'), f.name])}
               for f in resulting_files]

    results = {'results': options}
    return json.dumps(results)


@dajaxice_register()
def directories_autocomplete(request, search_term):
    """
    Provides the autocomplete backend for the directories dropdown in the policy view.

    Args:
        request (request):
            The django request object.

        search_term (str):
            The search term, should be a filename or path or a combination.

    Returns:
        A json object in the following form, eg.:
            {
                result: [
                    {id: 758, 'text': '/bin'},
                    {id: 65, 'text': '/etc'}
                ]
            }


    This ajax function, especially the result format is made to work with
    the autocomplete feature of the jQuery plugin Select2: http://ivaynberg.github.io/select2/

    """
    dirs = models.Directory.objects.filter(path__icontains=search_term)
    results = {'results': [{'id': d.id, 'directory': d.path} for d in dirs]}
    return json.dumps(results)


@dajaxice_register()
def paging(request, template, list_producer, stat_producer, var_name,
           current_page, page_size, filter_query):
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
    }

    # register stat producer
    stat_producer_dict = {
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

    # render the given template with the element list to a html string
    response = {
        'current_page': current_page,
        'page_count': page_count,
        'html': render_to_string(template + '.html', {var_name: element_list})
    }

    return json.dumps(response)
