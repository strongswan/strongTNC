# -*- coding: utf-8 -*-
"""
Custom manage.py command to import swid tags from a file.

Usage: ./manage.py importswid [filename]

The file must contain valid swid tags, one swid tag per line, separated by a **single** newline.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

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
            raise CommandError('Usage: ./manage.py importswid <filename>')

        filename = args[0]

        if not os.path.isfile(filename):
            raise CommandError('No such file: ' + filename)

        encoding = self.stdout.encoding or 'ascii'
        with open(filename, 'r') as f:
            for line in f:
                tag_xml = line.strip().decode('utf8')
                tag, replaced = utils.process_swid_tag(tag_xml, allow_tag_update=True)
                if replaced:
                    self.stdout.write('Replaced {0}'.format(tag).encode(encoding, 'replace'))
                else:
                    self.stdout.write('Added {0}'.format(tag).encode(encoding, 'replace'))
