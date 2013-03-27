import base64
import simplejson
import binascii
from django.db import models
from django.utils.translation import ugettext_lazy as _

class BinaryField(models.Field):
    description = _("Raw binary data for SQLite")

    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        super(BinaryField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        """Internal database field type."""
        return 'blob'

class HashField(BinaryField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        return binascii.hexlify(value)

    def get_prep_value(self, value):
        return binascii.unhexlify(value)

class Action():
    NONE = 0
    ALLOW = 1
    ISOLATE = 2
    BLOCK = 3

class Device(models.Model):
    """
    An Android Device identified by its AndroidID
    """
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=50)
    description = models.CharField(default='', max_length=50, blank=True)

    def __unicode__(self):
        return '%s (%s)' % (self.description, self.value[:10])

    def getWorkItems(self):
        #Method won't work anymore
        raise NotImplementedError
        items = []
        for g in self.groups.all():
            items += g.enforcements.all()

        workitems = []
        for i in set(items):
            workitems.append(i.policy.getWorkItem())

        return workitems

    class Meta:
        db_table = u'devices'

class Group(models.Model):
    """
    Management group of devices
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=50)
    members = models.ManyToManyField(Device, related_name='groups')
    parent = models.ForeignKey('self', related_name='membergroups', null=True,
            blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'groups'

class Product(models.Model):
    """
    Platform (f.e Android or Ubuntu)
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def __json__(self):
        return simplejson.dumps({
            'id': self.id,
            'name': self.name
            })

    class Meta:
        db_table = u'products'

#class DeviceInfo(models.Model):
#    """
#    Result of a TNC health check
#    """
#    id = models.AutoField(primary_key = True)
#    device = models.ForeignKey(Device, db_column='device', related_name='logins')
#    time = models.IntegerField()
#    product = models.ForeignKey(Product, db_column = 'product')
#    packagecount = models.IntegerField(default = 0, blank = True,
#            db_column = 'count')
#    count_update = models.IntegerField(default = 0, blank = True)
#    count_blacklist = models.IntegerField(default = 0, blank = True)
#    flags = models.IntegerField(default = 0, blank = True)
#    class Meta:
#        db_table = u'device_infos'
#        unique_together = (('device','time'))

class Directory(models.Model):
    """
    Unix-style directory path
    """
    id = models.AutoField(primary_key=True)
    path = models.CharField(unique=True, max_length=500)

    def __unicode__(self):
        return self.path

    class Meta:
        db_table = u'directories'
    

class File(models.Model):
    """
    Filename
    """
    id = models.AutoField(primary_key=True)
    directory = models.ForeignKey(Directory, db_column='dir', related_name='files')
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return '%s/%s' % (self.directory.path, self.name)

    def __json__(self):
        return simplejson.dumps({
            'id' : self.id,
            'name' : self.name,
            })

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

    def __json__(self):
        return simplejson.dumps({
            'id' : self.id,
            'name' : self.name,
            })

    class Meta:
        db_table = u'algorithms'

class FileHash(models.Model):
    """
    SHA-1 or similar filehash
    """
    id = models.AutoField(primary_key=True)
    file = models.ForeignKey(File, db_column='file', related_name='hashes')
    product = models.ForeignKey(Product, db_column='product')
    key = models.IntegerField(null=False, default=0)
    algorithm = models.ForeignKey(Algorithm, db_column='algo')
    hash = HashField(db_column='hash')

    class Meta:
        db_table = u'file_hashes'

    def __unicode__(self):
        return '%s (%s)' % (self.hash, self.algorithm)

    def __json__(self):
        return simplejson.dumps({
            'file' : self.file.__json__(),
            'product' : self.product.__json__(),
            'key' : self.key,
            'algo' : self.algorithm.__json__(),
            'hash' : base64.encodestring(self.hash.__str__()),
            })


class Package(models.Model):
    """
    aptitude Package name
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'packages'

class Version(models.Model):
    """
    Version number string of a package
    """
    id = models.AutoField(primary_key=True)
    package = models.ForeignKey(Package, db_column='package')
    product = models.ForeignKey(Product, related_name='versions',
            db_column='product')
    release = models.CharField(blank=False, max_length=100)
    security = models.BooleanField(null=False)
    time = models.DateTimeField()

    def __unicode__(self):
        return self.release

    class Meta:
        db_table = u'versions'

class DeviceLog(models.Model):
    """
    History of logins per device
    """
    id = models.AutoField(primary_key=True)
    device = models.ForeignKey(Device, related_name='log')
    time = models.DateTimeField()
    result = models.CharField(max_length=20, null=False)
    score = models.IntegerField(null=False, blank=True)

    class Meta:
        db_table = u'device_logs'

class Policy(models.Model):
    """
    Instance of a policy. Defines a specific check
    """
    id = models.AutoField(primary_key=True)
    type = models.IntegerField()
    name = models.CharField(unique=True, max_length=100)
    argument = models.CharField(max_length=500, blank=True)
    fail = models.IntegerField(blank=True)
    default = models.IntegerField(blank=True)

    def __unicode__(self):
        return self.name

    def getWorkItem(self):
        raise NotImplementedError

    class Meta:
        db_table = u'policies'
        verbose_name_plural = 'Policies'

class Enforcement(models.Model):
    """
    Rule to enforce a policy on a group
    """
    id = models.AutoField(primary_key=True)
    policy = models.ForeignKey(Policy, related_name='enforcements')
    group = models.ForeignKey(Group, related_name='enforcements')
    max_age = models.IntegerField()
    fail = models.IntegerField(blank=True)
    default = models.IntegerField(blank=True)

    def __unicode__(self):
        return '%s on %s' % (self.policy.name, self.group.name)

    class Meta:
        db_table = u'enforcements'
        unique_together = (('policy','group'))

class WorkItem(models.Model):
    id = models.AutoField(primary_key=True)
    policy = models.ForeignKey(Policy)
    device = models.ForeignKey(Device, related_name='workitems')
    type = models.IntegerField(null=False, blank=False)
    argument = models.CharField(max_length=500)
    fail = models.IntegerField(blank=True)
    default = models.IntegerField(blank=True)
    error = models.IntegerField(blank=True)
    recommendation = models.IntegerField(blank=True)

    class Meta:
        db_table = u'workitems'

class Result(models.Model):
    id = models.AutoField(primary_key=True)
    device = models.ForeignKey(Device)
    policy = models.ForeignKey(Policy)
    last_check = models.DateTimeField()
    error = models.IntegerField(null=False, blank=True)
    recommendation = models.IntegerField()

    class Meta:
        db_table = u'results'

class Identity(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.IntegerField()
    data = models.TextField()

    class Meta:
        db_table = u'identities'
