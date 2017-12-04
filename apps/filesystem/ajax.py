# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import json

from django.http import HttpResponse
from django.views.decorators.http import require_POST

from apps.core.decorators import ajax_login_required
from .models import File, Directory


@require_POST
@ajax_login_required
def files_autocomplete(request):
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
    search_term = request.POST.get('search_term')
    resulting_files = File.filter(search_term)

    # create resulting json to return
    options = [{'id': f.id, 'file': '/'.join([f.directory.path.rstrip('/'), f.name])}
               for f in resulting_files]

    results = {'results': options}
    return HttpResponse(json.dumps(results), content_type="application/x-json")


@require_POST
@ajax_login_required
def directories_autocomplete(request):
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
    search_term = request.POST.get('search_term')
    dirs = Directory.objects.filter(path__icontains=search_term)
    results = {'results': [{'id': d.id, 'directory': d.path} for d in dirs]}
    return HttpResponse(json.dumps(results), content_type="application/x-json")
