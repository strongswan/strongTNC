# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json
import os.path
from datetime import datetime

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
