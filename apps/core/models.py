# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models

from . import fields
from . import types


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
        ordering = ('data',)

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
    time = fields.EpochField()
    connection_id = models.IntegerField(db_column='connection')
    identity = models.ForeignKey(Identity, related_name='sessions', db_column='identity')
    device = models.ForeignKey('devices.Device', related_name='sessions', db_column='device')
    recommendation = models.IntegerField(db_column='rec', null=True, choices=types.ACTION_CHOICES)

    class Meta:
        db_table = u'sessions'
        get_latest_by = 'time'
        ordering = ('-time',)

    def __unicode__(self):
        return 'Session %s by %s' % (self.pk, self.identity)

    def list_repr(self):
        """
        String representation in lists
        """
        return 'Session %s by %s' % (self.pk, self.identity)


class WorkItem(models.Model):
    """
    A workitem representing a task for an IMV
    """
    enforcement = models.ForeignKey('policies.Enforcement', db_column='enforcement',
            related_name="workitems")
    session = models.ForeignKey(Session, db_column='session', related_name='workitems')
    type = models.IntegerField(null=False, blank=False, choices=types.WORKITEM_TYPE_CHOICES)
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
    policy = models.ForeignKey('policies.Policy', db_column='policy', related_name='results')
    result = models.TextField()
    recommendation = models.IntegerField(db_column='rec', choices=types.ACTION_CHOICES)

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
