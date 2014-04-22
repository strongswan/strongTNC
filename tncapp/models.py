# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import binascii
import calendar
from datetime import datetime, timedelta

from django.utils import timezone
from django.db import models

import pytz


class BinaryField(models.Field):
    """
    Custom field type for Binary data
    """
    description = "Raw binary data for SQLite"

    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        super(BinaryField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        """Internal database field type."""
        return 'blob'


class HashField(BinaryField):
    """
    Custom field type to display file hashes
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        return binascii.hexlify(value)

    def get_prep_value(self, value):
        return binascii.unhexlify(value)


class EpochField(models.IntegerField):
    """
    Custom field type for unix timestamps.
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, int):
            dt = datetime.utcfromtimestamp(value)
            return dt.replace(tzinfo=pytz.utc)  # Make datetime timezone-aware
        elif isinstance(value, datetime):
            return value
        elif value is None:
            return None
        else:
            raise ValueError('Invalid type for epoch field: %s' % type(value))

    def get_prep_value(self, value):
        if value:
            return calendar.timegm(value.utctimetuple())
        return None


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


class Product(models.Model):
    """
    The platform (e.g. Android or Ubuntu).
    """
    name = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'products'


class Regid(models.Model):
    """
    SWID Registration ID.

    DEPRECATED, will be replaced with SWID tables.

    """
    name = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'regids'


class Tag(models.Model):
    """
    SWID Tag.

    DEPRECATED, will be replaced with SWID tables.

    """
    regid = models.ForeignKey(Regid, db_column='regid', related_name='tags')
    unique_sw_id = models.TextField(db_index=True)
    value = models.TextField()

    def __unicode__(self):
        return '%s_%s' % (self.regid.name, self.unique_sw_id)

    class Meta:
        db_table = 'tags'


class Device(models.Model):
    """
    An Android Device identified by its AndroidID.
    """
    value = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True, default='')
    product = models.ForeignKey(Product, related_name='devices', db_column='product')
    trusted = models.IntegerField(default=0)
    created = EpochField(null=True, blank=True)

    def __unicode__(self):
        if self.description:
            return '%s (%s)' % (self.description, self.value[:10])
        else:
            return self.value

    def get_group_set(self):
        """
        Get all groups of the device
        """
        groups = []
        for g in self.groups.all():
            groups.append(g)
            groups += g.get_parents()

        groups = set(groups)
        return groups

    def get_inherit_set(self):
        """
        Get the groups which the device has inherited
        """
        group_set = self.get_group_set()
        for group in (group_set & set(self.groups.all())):
            group_set.remove(group)

        return group_set

    def is_due_for(self, enforcement):
        """
        Check if the device needs to perform the measurement defined by the
        enforcement
        """
        try:
            result = Result.objects.filter(session__device=self,
                                           policy=enforcement.policy).latest()
        except Result.DoesNotExist:
            return True

        deadline = timezone.now() - timedelta(seconds=enforcement.max_age)

        if result.session.time < deadline or (result.recommendation != Action.ALLOW):
            return True

        return False

    def create_work_items(self, session):
        """
        Creates workitems for every policy that is due
        """

        enforcements = []
        for group in self.get_group_set():
            enforcements += group.enforcements.all()

        minforcements = []

        while enforcements:
            emin = enforcements.pop()
            for e in enforcements:
                if emin.policy == e.policy:
                    emin = min(emin, e, key=lambda x: x.max_age)
                    if emin == e:
                        enforcements.remove(e)

            minforcements.append(emin)

        for enforcement in minforcements:
            if self.is_due_for(enforcement):
                enforcement.policy.create_work_item(enforcement, session)

    class Meta:
        db_table = 'devices'


class Group(models.Model):
    """
    Group of devices, for management purposes.
    """
    name = models.CharField(max_length=50)
    devices = models.ManyToManyField(Device, related_name='groups', blank=True, db_table='groups_members')
    product_defaults = models.ManyToManyField(Product, related_name='default_groups', blank=True)
    parent = models.ForeignKey('self', related_name='membergroups', null=True,
            blank=True, db_column='parent')

    class Meta:
        db_table = 'groups'

    def get_parents(self):
        """
        Recursively get all parent groups.
        """
        if not self.parent:
            return []
        return [self.parent] + self.parent.get_parents()

    def __unicode__(self):
        return self.name


class Directory(models.Model):
    """
    Unix-style directory path.
    """
    path = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.path

    class Meta:
        db_table = 'directories'
        verbose_name_plural = 'directories'


class File(models.Model):
    """
    A file in a directory.
    """
    name = models.CharField(max_length=255, db_index=True)
    directory = models.ForeignKey(Directory, db_column='dir')

    def __unicode__(self):
        return '%s/%s' % (self.directory.path, self.name)

    class Meta:
        db_table = 'files'


class Algorithm(models.Model):
    """
    A hashing algorithm.
    """
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'algorithms'


class FileHash(models.Model):
    """
    A file hash.
    """
    file = models.ForeignKey(File, db_column='file')
    product = models.ForeignKey(Product, db_column='product')
    device = models.IntegerField(null=False, default=0)  # TODO convert to nullable(?) FK
    algorithm = models.ForeignKey(Algorithm, db_column='algo', on_delete=models.PROTECT)
    hash = HashField(db_column='hash')

    class Meta:
        db_table = 'file_hashes'
        verbose_name_plural = 'file hashes'

    def __unicode__(self):
        return '%s (%s)' % (self.hash, self.algorithm)


class Package(models.Model):
    """
    A Package.
    """
    name = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'packages'


class Version(models.Model):
    """
    Version number string of a package.
    """
    package = models.ForeignKey(Package, db_column='package', related_name='versions')
    product = models.ForeignKey(Product, db_column='product', related_name='versions')
    release = models.CharField(max_length=255, db_index=True)
    security = models.BooleanField(default=0)
    blacklist = models.IntegerField(null=True, blank=True)
    time = EpochField()

    def __unicode__(self):
        return self.release

    class Meta:
        db_table = 'versions'
        index_together = [('package', 'product')]


class Policy(models.Model):
    """
    Instance of a policy. Defines a specific check.
    """
    type = models.IntegerField()
    name = models.CharField(unique=True, max_length=100)
    argument = models.TextField(null=True)
    fail = models.IntegerField(blank=True, db_column='rec_fail', choices=ACTION_CHOICES)
    noresult = models.IntegerField(blank=True, db_column='rec_noresult', choices=ACTION_CHOICES)
    file = models.ForeignKey(File, null=True, blank=True,
            related_name='policies', on_delete=models.PROTECT,
            db_column='file')
    dir = models.ForeignKey(Directory, null=True, blank=True,
            related_name='policies', on_delete=models.PROTECT, db_column='dir')

    def create_work_item(self, enforcement, session):
        """
        Generate a workitem for a session.

        TODO do we even need to create workitems?

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

    def __unicode__(self):
        return self.name

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

    class Meta:
        db_table = 'policies'
        verbose_name_plural = 'Policies'


class Enforcement(models.Model):
    """
    Rule to enforce a policy on a group.
    """
    policy = models.ForeignKey(Policy, related_name='enforcements', db_column='policy')
    group = models.ForeignKey(Group, related_name='enforcements', db_column='group_id')
    max_age = models.IntegerField()
    fail = models.IntegerField(db_column='rec_fail', null=True, blank=True,
            choices=ACTION_CHOICES)
    noresult = models.IntegerField(db_column='rec_noresult', null=True, blank=True,
            choices=ACTION_CHOICES)

    def __unicode__(self):
        return '%s on %s' % (self.policy.name, self.group.name)

    class Meta:
        db_table = 'enforcements'
        unique_together = [('policy', 'group')]


class Identity(models.Model):
    """
    A user identity.
    """
    type = models.IntegerField()
    data = models.TextField(db_column='value')

    def __unicode__(self):
        return self.data

    class Meta:
        db_table = 'identities'
        unique_together = [('type', 'data')]
        verbose_name_plural = 'identities'


class Session(models.Model):
    """
    Result of a TNC session.
    """
    time = EpochField()
    connection_id = models.IntegerField(db_column='connection')
    identity = models.ForeignKey(Identity, related_name='sessions', db_column='identity')
    device = models.ForeignKey(Device, related_name='sessions', db_column='device')
    recommendation = models.IntegerField(db_column='rec', null=True, choices=ACTION_CHOICES)

    def __unicode__(self):
        return 'Session %s by %s' % (self.connection_id, self.identity)

    class Meta:
        db_table = 'sessions'


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


# EXTRA TABLES, TODO REMOVE AFTER STRONGSWAN / STRONGTNC SPLIT

class Component(models.Model):
    vendor_id = models.IntegerField()
    name = models.IntegerField()
    qualifier = models.IntegerField(default=0)
    label = models.CharField(max_length=255)

    class Meta:
        db_table = 'components'


class ComponentHash(models.Model):
    # TODO missing "id" primary key in database
    component = models.ForeignKey(Component)
    device = models.ForeignKey(Device, db_column='key')
    seq_no = models.IntegerField()
    pcr = models.IntegerField()
    algorithm = models.ForeignKey(Algorithm, db_column='algo')
    hash = HashField()

    class Meta:
        db_table = 'component_hashes'
        verbose_name_plural = 'component hashes'
