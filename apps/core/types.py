# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals


class Action(object):
    """
    Possible recommendation values
    """
    ALLOW = 0
    BLOCK = 1
    ISOLATE = 2
    NONE = 3


ACTION_CHOICES = (
    (Action.ALLOW, 'Allow'),
    (Action.BLOCK, 'Block'),
    (Action.ISOLATE, 'Isolate'),
    (Action.NONE, 'None'),
)


class WorkItemType(object):
    """
    Possible workitem type values
    """
    RESVD = 0
    PCKGS = 1
    UNSRC = 2
    FWDEN = 3
    PWDEN = 4
    FREFM = 5
    FMEAS = 6
    FMETA = 7
    DREFM = 8
    DMEAS = 9
    DMETA = 10
    TCPOP = 11
    TCPBL = 12
    UDPOP = 13
    UDPBL = 14
    SWIDT = 15
    TPMRA = 16


WORKITEM_TYPE_CHOICES = (
    (WorkItemType.RESVD, 'RESVD'),
    (WorkItemType.PCKGS, 'PCKGS'),
    (WorkItemType.UNSRC, 'UNSRC'),
    (WorkItemType.FWDEN, 'FWDEN'),
    (WorkItemType.PWDEN, 'PWDEN'),
    (WorkItemType.FREFM, 'FREFM'),
    (WorkItemType.FMEAS, 'FMEAS'),
    (WorkItemType.FMETA, 'FMETA'),
    (WorkItemType.DREFM, 'DREFM'),
    (WorkItemType.DMEAS, 'DMEAS'),
    (WorkItemType.DMETA, 'DMETA'),
    (WorkItemType.TCPOP, 'TCPOP'),
    (WorkItemType.TCPBL, 'TCPBL'),
    (WorkItemType.UDPOP, 'UDPOP'),
    (WorkItemType.UDPBL, 'UDPBL'),
    (WorkItemType.SWIDT, 'SWIDT'),
    (WorkItemType.TPMRA, 'TPMRA'),
)
