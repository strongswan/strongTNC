#
# Copyright (C) 2013 Andreas Steffen
# Copyright (C) 2013 Marco Tanner
# HSR University of Applied Sciences Rapperswil
#
# This file is part of strongTNC.  strongTNC is free software: you can
# redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# strongTNC is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with strongTNC.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Defines model classes which are used by the Django OR-mapper
"""

import binascii
from datetime import datetime
from datetime import timedelta
from calendar import timegm
from django.db import models

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
    Custom field type for unix timestamps
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if type(value) == int:
            return datetime.utcfromtimestamp(float(value))
        else:
            if type(value) == datetime:
                return value

    def get_prep_value(self, value):
        if value:
            return timegm(value.utctimetuple())
        return None

class Action(object):
    """
    Possible recommendation values
    """
    ALLOW = 0
    BLOCK = 1
    ISOLATE = 2
    NONE = 3

class WorkItemType(object):
    """
    Possible workitem type values
    """
    RESVD =  0
    PCKGS =  1
    UNSRC =  2
    FWDEN =  3
    PWDEN =  4
    FREFM =  5
    FMEAS =  6
    FMETA =  7
    DREFM =  8
    DMEAS =  9
    DMETA = 10
    TCPOP = 11
    TCPBL = 12
    UDPOP = 13
    UDPBL = 14
    SWIDT = 15
    TPMRA = 16

class Product(models.Model):
    """
    Platform (f.e Android or Ubuntu)
    """
    id = models.AutoField(primary_key=True)
    name = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'products'

class Regid(models.Model):
    """
    SWID Registration ID
    """
    id = models.AutoField(primary_key=True)
    name = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'regids'

class Tag(models.Model):
    """
    SWID Tag
    """
    id = models.AutoField(primary_key=True)
    regid = models.ForeignKey(Regid, db_column='regid',
            related_name='tags', on_delete=models.CASCADE)
    unique_sw_id = models.TextField()
    value = models.TextField()

    def __unicode__(self):
        return '%s_%s' % (self.regid.name, self.unique_sw_id)

    class Meta:
        db_table = u'tags'

class Device(models.Model):
    """
    An Android Device identified by its AndroidID
    """
    id = models.AutoField(primary_key=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Product, related_name='devices', db_column='product')
    created = EpochField(null=True,blank=True)


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

        deadline = datetime.today() - timedelta(seconds=enforcement.max_age)

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

        minforcements=[]

        while enforcements:
            emin = enforcements.pop()
            for e in enforcements:
                if emin.policy == e.policy:
                    emin = min(emin,e, key=lambda x: x.max_age)
                    if emin == e:
                        enforcements.remove(e)

            minforcements.append(emin)

        for enforcement in minforcements:
            if self.is_due_for(enforcement):
                enforcement.policy.create_work_item(enforcement, session)

    class Meta:
        db_table = u'devices'

class Group(models.Model):
    """
    Management group of devices
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(Device, related_name='groups', blank=True)
    product_defaults = models.ManyToManyField(Product, related_name='default_groups', blank=True)
    parent = models.ForeignKey('self', related_name='membergroups', null=True,
            blank=True, on_delete=models.CASCADE, db_column='parent')

    def __unicode__(self):
        return self.name

    def get_parents(self):
        """
        Recursively get all parent groups
        """
        if not self.parent:
            return []

        return [self.parent] + self.parent.get_parents()

    class Meta:
        db_table = u'groups'

class Directory(models.Model):
    """
    Unix-style directory path
    """
    id = models.AutoField(primary_key=True)
    path = models.TextField(unique=True)

    def __unicode__(self):
        return self.path

    class Meta:
        db_table = u'directories'


class File(models.Model):
    """
    Filename
    """
    id = models.AutoField(primary_key=True)
    directory = models.ForeignKey(Directory, db_column='dir',
            related_name='files', on_delete=models.CASCADE)
    name = models.TextField()

    def __unicode__(self):
        return '%s/%s' % (self.directory.path, self.name)

    class Meta:
        db_table = u'files'

class Algorithm(models.Model):
    """
    A hashing algorithm
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, blank=False, max_length=20)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'algorithms'

class FileHash(models.Model):
    """
    SHA-1 or similar filehash
    """
    id = models.AutoField(primary_key=True)
    file = models.ForeignKey(File, db_column='file', related_name='hashes',
            on_delete=models.CASCADE)
    product = models.ForeignKey(Product, db_column='product')
    key = models.IntegerField(null=False, default=0)
    algorithm = models.ForeignKey(Algorithm, db_column='algo',
            on_delete=models.PROTECT)
    hash = HashField(db_column='hash')

    class Meta:
        db_table = u'file_hashes'

    def __unicode__(self):
        return '%s (%s)' % (self.hash, self.algorithm)

class Package(models.Model):
    """
    aptitude Package name
    """
    id = models.AutoField(primary_key=True)
    name = models.TextField(unique=True)
    blacklist = models.IntegerField(blank=True, default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'packages'

class Version(models.Model):
    """
    Version number string of a package
    """
    id = models.AutoField(primary_key=True)
    package = models.ForeignKey(Package, db_column='package',
            on_delete=models.CASCADE, related_name='versions')
    product = models.ForeignKey(Product, related_name='versions',
            db_column='product', on_delete=models.CASCADE)
    release = models.TextField()
    security = models.BooleanField(default=0)
    time = EpochField()
    blacklist = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.release

    class Meta:
        db_table = u'versions'

class Policy(models.Model):
    """
    Instance of a policy. Defines a specific check
    """
    id = models.AutoField(primary_key=True)
    type = models.IntegerField()
    name = models.CharField(unique=True, max_length=100)
    argument = models.TextField(null='True')
    fail = models.IntegerField(blank=True, db_column='rec_fail')
    noresult = models.IntegerField(blank=True, db_column='rec_noresult')
    file = models.ForeignKey(File, null=True, blank=True,
            related_name='policies', on_delete=models.PROTECT,
            db_column='file')
    dir = models.ForeignKey(Directory, null=True, blank=True,
            related_name='policies', on_delete=models.PROTECT, db_column='dir')

    def create_work_item(self, enforcement, session):
        """
        Generate a workitem for a session
        """
        item = WorkItem(result=None, type=self.type, recommendation=None,
                file=self.file, dir=self.dir, argument=self.argument,
                enforcement=enforcement, session=session)

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


    argument_funcs = {
            'Deny': lambda policy: '',
            'Installed Packages': lambda policy: '',
            'Unknown Source': lambda policy: '',
            'Forwarding Enabled': lambda policy: '',
            'Default Password Enabled': lambda policy: '',
            'File Reference Measurement': lambda policy: '',
            'File Measurement':lambda policy:  '',
            'File Metadata': lambda policy: '',
            'Directory Reference Measurement': lambda policy: '',
            'Directory Measurement': lambda policy: '',
            'Directory Metadata': lambda policy: '',
            'Open TCP Listening Ports': lambda p: p.argument if p.argument else '',
            'Blocked TCP Listening Ports': lambda p: p.argument if p.argument else '',
            'Open UDP Listening Ports': lambda p: p.argument if p.argument else '',
            'Blocked UDP Listening Ports': lambda p: p.argument if p.argument else '',
            'SWID Tag Inventory': lambda p: p.argument if p.argument else '',
            'TPM Remote Attestation': lambda p: p.argument if p.argument else '',
            }


    class Meta:
        db_table = u'policies'
        verbose_name_plural = 'Policies'

class Enforcement(models.Model):
    """
    Rule to enforce a policy on a group
    """
    id = models.AutoField(primary_key=True)
    policy = models.ForeignKey(Policy, related_name='enforcements',
            on_delete=models.CASCADE, db_column='policy')
    group = models.ForeignKey(Group, related_name='enforcements',
            on_delete=models.CASCADE, db_column='group_id')
    max_age = models.IntegerField()
    fail = models.IntegerField(null=True,blank=True, db_column='rec_fail')
    noresult = models.IntegerField(null=True,blank=True, db_column='rec_noresult')

    def __unicode__(self):
        return '%s on %s' % (self.policy.name, self.group.name)

    class Meta:
        db_table = u'enforcements'
        unique_together = (('policy','group'))

class Identity(models.Model):
    """
    A user identity
    """
    id = models.AutoField(primary_key=True)
    data = models.TextField(db_column='value')

    class Meta:
        db_table = u'identities'

class Session(models.Model):
    """Result of a TNC session."""
    id = models.AutoField(primary_key=True)
    connectionID = models.IntegerField(db_column='connection')
    device = models.ForeignKey(Device, related_name='sessions',
       	     on_delete=models.CASCADE, db_column='device')
    identity = models.ForeignKey(Identity, related_name='sessions',
               on_delete=models.CASCADE, db_column='identity')
    time = EpochField()
    recommendation = models.IntegerField(null=True, db_column='rec')

    class Meta:
        db_table = u'sessions'

class WorkItem(models.Model):
    """
    A workitem representing a task for an IMV
    """
    id = models.AutoField(primary_key=True)
    enforcement = models.ForeignKey(Enforcement, db_column='enforcement',
                  related_name="workitems", on_delete=models.CASCADE)
    session = models.ForeignKey(Session, db_column='session',
                  related_name='workitems', on_delete=models.CASCADE)
    type = models.IntegerField(null=False, blank=False)
    argument = models.TextField()
    fail = models.IntegerField(null=True,blank=True)
    noresult = models.IntegerField(null=True,blank=True)
    result = models.TextField(null=True)
    recommendation = models.IntegerField(null=True,blank=True)

    #Foreign Keys for FileHash, DirHash, FileExist, FileNotExist
    file = models.ForeignKey(File, null=True, on_delete=models.DO_NOTHING)
    dir = models.ForeignKey(Directory, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = u'workitems'

class Result(models.Model):
    """
    A result of a measurement
    """
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, db_column='session',
            on_delete=models.CASCADE, related_name='results')
    policy = models.ForeignKey(Policy, db_column='policy',
            on_delete=models.CASCADE, related_name='results')
    result = models.TextField()
    recommendation = models.IntegerField(db_column='rec')

    class Meta:
        db_table = u'results'
        get_latest_by = 'session__time'

