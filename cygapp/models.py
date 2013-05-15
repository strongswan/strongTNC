import binascii
from datetime import datetime
from django.db import models

class BinaryField(models.Field):
    description = "Raw binary data for SQLite"

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

class Action(object):
    NONE = 0
    ALLOW = 1
    ISOLATE = 2
    BLOCK = 3

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

class Device(models.Model):
    """
    An Android Device identified by its AndroidID
    """
    id = models.AutoField(primary_key=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Product, related_name='devices')
    created = models.DateTimeField(null=True,blank=True)


    def __unicode__(self):
        if self.description:
            return '%s (%s)' % (self.description, self.value[:10])
        else:
            return self.value

    def get_group_set(self):
        groups = []
        for g in self.groups.all():
            groups.append(g)
            groups += g.get_parents()

        groups = set(groups)
        return groups

    def is_due_for(self, enforcement):
        try:
            last_meas = Session.objects.filter(device=self).latest('time')
            result = Result.objects.get(session=last_meas,
                    policy=enforcement.policy)
        except Session.DoesNotExist:
            return True
        except Result.DoesNotExist:
            return True

        age = datetime.today() - last_meas.time

        if age.days >= enforcement.max_age or (result.recommendation !=
                Action.ALLOW):
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
    name = models.CharField(unique=True, max_length=50)
    members = models.ManyToManyField(Device, related_name='groups',blank=True)
    product_defaults = models.ManyToManyField(Product, related_name='default_groups', blank=True)
    parent = models.ForeignKey('self', related_name='membergroups', null=True,
            blank=True, on_delete=models.CASCADE, db_column='parent')

    def __unicode__(self):
        return self.name

    def get_parents(self):
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
        return self.name[14:] # name - 'PTS_MEAS_ALGO_'

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
    time = models.DateTimeField()
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
    fail = models.IntegerField(blank=True)
    noresult = models.IntegerField(blank=True)
    file = models.ForeignKey(File, null=True, blank=True,
            related_name='policies', on_delete=models.PROTECT,
            db_column='file')
    dir = models.ForeignKey(Directory, null=True, blank=True,
            related_name='policies', on_delete=models.PROTECT, db_column='dir')

    def create_work_item(self, enforcement, session):
        item = WorkItem()
        item.result = None
        item.type = self.type
        item.recommendation = None
        item.argument = self.argument
        item.enforcement = enforcement
        item.session = session
        
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
            'NONE',
            'ALLOW',
            'ISOLATE',
            'BLOCK',
            ]

    types = [
            'FileHash',
            'DirHash',
            'ListeningPortTCP',
            'ListeningPortUDP',
            'FileExist',
            'NotFileExist',
            'MissingUpdate',
            'MissingSecurityUpdate',
            'BlacklistedPackage',
            'OSSettings',
            'Deny',
            ]

    
    argument_funcs = {
            'FileHash': lambda policy: policy.file.id if policy.file else '',
            'DirHash': lambda policy: policy.dir.id if policy.dir else '',
            'ListeningPortTCP': lambda p: p.argument if p.argument else '',
            'ListeningPortUDP': lambda p: p.argument if p.argument else '',
            'FileExist': lambda policy: policy.file.id if policy.file else '',
            'NotFileExist': lambda policy: policy.file.id if policy.file else '',
            'MissingUpdate': lambda policy: '',
            'MissingSecurityUpdate':lambda policy:  '',
            'BlacklistedPackage': lambda policy: '',
            'OSSettings': lambda policy: '',
            'Deny': lambda policy: '',
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
            on_delete=models.CASCADE, db_column='group')
    max_age = models.IntegerField()
    fail = models.IntegerField(null=True,blank=True)
    noresult = models.IntegerField(null=True,blank=True)

    def __unicode__(self):
        return '%s on %s' % (self.policy.name, self.group.name)

    class Meta:
        db_table = u'enforcements'
        unique_together = (('policy','group'))

class Identity(models.Model):
    id = models.AutoField(primary_key=True)
    data = models.TextField()

    class Meta:
        db_table = u'identities'

class Session(models.Model):
    """Result of a TNC session."""
    id = models.AutoField(primary_key=True)
    connectionID = models.IntegerField()
    device = models.ForeignKey(Device, related_name='sessions',
        on_delete=models.CASCADE, db_column='device')
    identity = models.ForeignKey(Identity, related_name='sessions',
            on_delete=models.CASCADE, db_column='identity')
    time = models.DateTimeField()
    recommendation = models.IntegerField(null=True)

    class Meta:
        db_table = u'sessions'

class WorkItem(models.Model):
    id = models.AutoField(primary_key=True)
    enforcement = models.ForeignKey(Enforcement, on_delete=models.CASCADE,
            db_column='enforcement')
    session = models.ForeignKey(Session, db_column='session',
            related_name='workitems', on_delete=models.CASCADE)
    type = models.IntegerField(null=False, blank=False)
    argument = models.TextField()
    fail = models.IntegerField(null=True,blank=True)
    noresult = models.IntegerField(null=True,blank=True)
    result = models.TextField(null=True)
    recommendation = models.IntegerField(null=True,blank=True)

    class Meta:
        db_table = u'workitems'

class Result(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, db_column='session',
            on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, db_column='policy',
            on_delete=models.CASCADE)
    result = models.TextField()
    recommendation = models.IntegerField()

    class Meta:
        db_table = u'results'
        get_latest_by = 'session__time'

