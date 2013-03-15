import base64
import simplejson
from django.db import models

class Device(models.Model):
    """
    An Android Device identified by its AndroidID
    """
    id = models.AutoField(primary_key=True)
    value = models.TextField()
    description = models.TextField()

    class Meta:
        db_table = u'devices'

class Product(models.Model):
    """
    Platform (f.e Android or Ubuntu)
    """
    id = models.AutoField(primary_key=True)
    name = models.TextField()

    def __unicode__(self):
        return self.name

    def __json__(self):
        return simplejson.dumps({
            'id': self.id,
            'name': self.name
            })


    class Meta:
        db_table = u'products'

class DeviceInfo(models.Model):
    """
    Result of a TNC health check
    """
    id = models.AutoField(primary_key = True)
    device = models.ForeignKey(Device, db_column='device', related_name='logins')
    time = models.IntegerField()
    product = models.ForeignKey(Product, db_column = 'product')
    packagecount = models.IntegerField(default = 0, blank = True,
            db_column = 'count')
    count_update = models.IntegerField(default = 0, blank = True)
    count_blacklist = models.IntegerField(default = 0, blank = True)
    flags = models.IntegerField(default = 0, blank = True)
    class Meta:
        db_table = u'device_infos'
        unique_together = (('device','time'))

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
    directory = models.ForeignKey(Directory, db_column='dir', related_name='files')
    name = models.TextField()

    def __unicode__(self):
        return self.name

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
    name = models.TextField(null=False, blank=False)

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
    hash = models.TextField()

    class Meta:
        db_table = u'file_hashes'
        unique_together = (('file','product'))

    def __unicode__(self):
        return base64.encodestring(self.hash.__str__())

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
    name = models.TextField(unique=True)

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
    release = models.TextField(blank=False)
    security = models.BooleanField(null=False)
    time = models.DateTimeField()

    def __unicode__(self):
        return self.release

    class Meta:
        db_table = u'versions'

