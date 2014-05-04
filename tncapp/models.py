# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models

from apps.core.fields import EpochField


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


class Policy(models.Model):
    """
    Instance of a policy. Defines a specific check.
    """
    type = models.IntegerField()
    name = models.CharField(unique=True, max_length=100)
    argument = models.TextField(null=True)
    fail = models.IntegerField(db_column='rec_fail', choices=ACTION_CHOICES)
    noresult = models.IntegerField(db_column='rec_noresult', choices=ACTION_CHOICES)
    file = models.ForeignKey('filesystem.File', null=True, blank=True,
            related_name='policies', on_delete=models.PROTECT,
            db_column='file')
    dir = models.ForeignKey('filesystem.Directory', null=True, blank=True,
            related_name='policies', on_delete=models.PROTECT, db_column='dir')

    class Meta:
        db_table = 'policies'
        verbose_name_plural = 'Policies'

    def __unicode__(self):
        return self.name

    def list_repr(self):
        """
        String representation in lists
        """
        return self.name

    def create_work_item(self, enforcement, session):
        """
        Generate a workitem for a session.

        """
        item = WorkItem(result=None, type=self.type, recommendation=None,
                arg_str=self.argument, enforcement=enforcement, session=session)

        item.fail = self.fail
        if enforcement.fail is not None:
            item.fail = enforcement.fail

        item.noresult = self.noresult
        if enforcement.noresult is not None:
            item.noresult = enforcement.noresult

        item.save()

    action = [
        'ALLOW',
        'BLOCK',
        'ISOLATE',
        'NONE',
    ]

    # TODO create CHOICES from this, use get_types_display()
    types = [
        'Deny',
        'Installed Packages',
        'Unknown Source',
        'Forwarding Enabled',
        'Default Password Enabled',
        'File Reference Measurement',
        'File Measurement',
        'File Metadata',
        'Directory Reference Measurement',
        'Directory Measurement',
        'Directory Metadata',
        'Open TCP Listening Ports',
        'Blocked TCP Listening Ports',
        'Open UDP Listening Ports',
        'Blocked UDP Listening Ports',
        'SWID Tag Inventory',
        'TPM Remote Attestation',
    ]

    swid_request_flags = [
        'R',
        'S',
        'C',
    ]

    tpm_attestation_flags = [
        'B',
        'I',
        'T',
    ]

    argument_funcs = {
        'Deny': lambda policy: '',
        'Installed Packages': lambda policy: '',
        'Unknown Source': lambda policy: '',
        'Forwarding Enabled': lambda policy: '',
        'Default Password Enabled': lambda policy: '',
        'File Reference Measurement': lambda policy: '',
        'File Measurement': lambda policy: '',
        'File Metadata': lambda policy: '',
        'Directory Reference Measurement': lambda policy: '',
        'Directory Measurement': lambda policy: '',
        'Directory Metadata': lambda policy: '',
        'Open TCP Listening Ports': lambda p: p.argument or '',
        'Blocked TCP Listening Ports': lambda p: p.argument or '',
        'Open UDP Listening Ports': lambda p: p.argument or '',
        'Blocked UDP Listening Ports': lambda p: p.argument or '',
        'SWID Tag Inventory': lambda p: p.argument or '',
        'TPM Remote Attestation': lambda p: p.argument or '',
    }


class Enforcement(models.Model):
    """
    Rule to enforce a policy on a group.
    """
    policy = models.ForeignKey(Policy, related_name='enforcements', db_column='policy')
    group = models.ForeignKey('devices.Group', related_name='enforcements', db_column='group_id')
    max_age = models.IntegerField()
    fail = models.IntegerField(db_column='rec_fail', null=True, blank=True,
            choices=ACTION_CHOICES)
    noresult = models.IntegerField(db_column='rec_noresult', null=True, blank=True,
            choices=ACTION_CHOICES)

    class Meta:
        db_table = 'enforcements'
        unique_together = [('policy', 'group')]

    def __unicode__(self):
        return '%s on %s' % (self.policy.name, self.group.name)

    def list_repr(self):
        """
        String representation in lists
        """
        return '%s on %s' % (self.policy.name, self.group.name)


class Identity(models.Model):
    """
    A user identity.
    """
    type = models.IntegerField()
    data = models.TextField(db_column='value')

    class Meta:
        db_table = 'identities'
        unique_together = [('type', 'data')]
        verbose_name_plural = 'identities'

    def __unicode__(self):
        return self.data

    def list_repr(self):
        """
        String representation in lists
        """
        return self.data


class Session(models.Model):
    """
    Result of a TNC session.
    """
    time = EpochField()
    connection_id = models.IntegerField(db_column='connection')
    identity = models.ForeignKey(Identity, related_name='sessions', db_column='identity')
    device = models.ForeignKey('devices.Device', related_name='sessions', db_column='device')
    recommendation = models.IntegerField(db_column='rec', null=True, choices=ACTION_CHOICES)

    class Meta:
        db_table = u'sessions'
        get_latest_by = 'time'
        ordering = ['-time']

    def __unicode__(self):
        return 'Session %s by %s' % (self.connection_id, self.identity)

    def list_repr(self):
        """
        String representation in lists
        """
        return 'Session %s by %s' % (self.connection_id, self.identity)


class WorkItem(models.Model):
    """
    A workitem representing a task for an IMV
    """
    enforcement = models.ForeignKey(Enforcement, db_column='enforcement', related_name="workitems")
    session = models.ForeignKey(Session, db_column='session', related_name='workitems')
    type = models.IntegerField(null=False, blank=False, choices=WORKITEM_TYPE_CHOICES)
    arg_str = models.TextField()
    arg_int = models.IntegerField(default=0)
    fail = models.IntegerField(null=True, blank=True, db_column='rec_fail')
    noresult = models.IntegerField(null=True, blank=True, db_column='rec_noresult')
    recommendation = models.IntegerField(null=True, blank=True, db_column='rec_final')
    result = models.TextField(null=True, blank=True, db_column='result')

    class Meta:
        db_table = 'workitems'

    def __unicode__(self):
        return 'Workitem %i of session %i, enforcement %s' % (self.pk, self.session.pk, self.enforcement)

    def list_repr(self):
        """
        String representation in lists
        """
        return 'Workitem %i' % self.pk


class Result(models.Model):
    """
    A result of a measurement.
    """
    session = models.ForeignKey(Session, db_column='session', related_name='results')
    policy = models.ForeignKey(Policy, db_column='policy', related_name='results')
    result = models.TextField()
    recommendation = models.IntegerField(db_column='rec')

    class Meta:
        db_table = 'results'
        get_latest_by = 'session__time'

    def __unicode__(self):
        return 'Result of Session %i: %s' % (self.session.pk, self.result)

    def list_repr(self):
        """
        String representation in lists
        """
        return 'Result of Session %i: %s' % (self.session.pk, self.result)
