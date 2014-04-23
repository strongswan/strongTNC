# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals
import json
import os.path

from dajaxice.decorators import dajaxice_register

from tncapp import models


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

    resulting_files = None

    # prepare results from collected data
    if files and not dirs:
        resulting_files = files

    if dirs and not files:
        resulting_files = models.File.objects.filter(directory__in=dirs)

    if dirs and files:
        resulting_files = files | models.File.objects.filter(directory__in=dirs)

    # create resulting json to return
    if resulting_files:
        options = [{'id': f.id, 'text': os.path.join(f.directory.path, f.name)} for f in resulting_files]
    else:
        options = []

    results = {'results': options}
    return json.dumps(results)
