# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

"""
Custom manage.py command to import swid tags from a file.

Usage: ./manage.py importswid [filename]

The file must contain valid swid tags, one swid tag per line, separated by a **single** newline.
"""

import os.path

from django.core.management.base import BaseCommand, CommandError
from apps.swid import utils


class Command(BaseCommand):
    """
    Required class to be recognized by manage.py.
    """
    args = '<filename>'
    help = 'Import SWID tags from a file into the DB. ' \
           'The file must contain one swid tag per line.'

    def handle(self, *args, **kwargs):
        if len(args) != 1:
            raise CommandError('Wrong argument count, command needs exactly one argument.')

        filename = args[0]

        if not os.path.isfile(filename):
            raise CommandError('No such file: ' + filename)

        with open(filename, 'r') as f:
            for line in f:
                utils.process_swid_tag(line.strip())