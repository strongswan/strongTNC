# -*- coding: utf-8 -*-
"""
Custom manage.py command to import swid tags from a file.

Usage: ./manage.py importswid [filename]

The file must contain valid swid tags, one swid tag per line, separated by a **single** newline.
"""
from __future__ import print_function, division, absolute_import, unicode_literals

import os.path

from django.core.management.base import BaseCommand, CommandError
from config.settings import USE_XMPP, XMPP_GRID
from apps.swid import utils
from apps.swid.xmpp_grid import XmppGridClient


class Command(BaseCommand):
    """
    Required class to be recognized by manage.py.
    """
    args = '<filename>'
    help = 'Import SWID tags from a file into the DB. ' \
           'The file must contain one swid tag per line.'

    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **kwargs):
        if len(args) != 1:
            raise CommandError('Usage: ./manage.py importswid <filename>')

        filename = args[0]

        if not os.path.isfile(filename):
            raise CommandError('No such file: ' + filename)

        # Publish SWID tags on XMPP-Grid?
        xmpp_connected = False
        if USE_XMPP:
            # Initialize XMPP client
            xmpp = XmppGridClient(XMPP_GRID['jid'], XMPP_GRID['password'],
                                  XMPP_GRID['pubsub_server'])
            xmpp.ca_certs = XMPP_GRID['cacert']
            xmpp.certfile = XMPP_GRID['certfile']
            xmpp.keyfile = XMPP_GRID['keyfile']
            xmpp.use_ipv6 = XMPP_GRID['use_ipv6']

            # Connect to the XMPP server and start processing XMPP stanzas.
            if xmpp.connect():
                xmpp.process()
                xmpp_connected = True
            else:
                self.stdout.write('Unable to connect to XMPP-Grid server.')

        with open(filename, 'r') as f:
            for line in f:
                tag_xml = line.strip()
                tag, replaced = utils.process_swid_tag(tag_xml, allow_tag_update=True)
                if replaced:
                    self.stdout.write('Replaced {0}'.format(tag))
                else:
                    self.stdout.write('Added {0}'.format(tag))
                if xmpp_connected:
                    xmpp.publish(XMPP_GRID['node_swidtags'], tag.software_id, tag.json())
        if xmpp_connected:
            xmpp.disconnect()
