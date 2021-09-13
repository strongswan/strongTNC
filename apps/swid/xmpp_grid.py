# -*- coding: utf-8 -*-
import sys

from sleekxmpp.clientxmpp import ClientXMPP
from sleekxmpp.xmlstream import ET


# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class XmppGridClient(ClientXMPP):

    def __init__(self, jid, password, pubsub_server):
        super(XmppGridClient, self).__init__(jid, password)

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0059')
        self.register_plugin('xep_0060')
        self.add_event_handler('session_start', self.start, threaded=True)
        self.pubsub_server = pubsub_server

    def start(self, event):
        self.get_roster()
        self.send_presence()

    def publish(self, node, item_id, item):
        json_xml = '<json xmlns="urn:xmpp:json:0">%s</json>' % item
        payload = ET.fromstring(json_xml)
        self['xep_0060'].publish(self.pubsub_server, node, id=item_id,
                                 payload=payload)
        print('Published item %s to %s' % (item_id, node))
