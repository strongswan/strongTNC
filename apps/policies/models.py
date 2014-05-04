# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models

from tncapp.models import WorkItem, ACTION_CHOICES


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
