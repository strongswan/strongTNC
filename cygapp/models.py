import base64
import simplejson
from django.db import models

class Device(models.Model):
    """
    An Android Device identified by its AndroidID
    """
    id = models.IntegerField(primary_key=True)
    value = models.TextField()
    description = models.TextField()

    class Meta:
        db_table = u'devices'

class Product(models.Model):
    """
    Android Platform
    """
    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'products'

class DeviceInfo(models.Model):
    """
    Result of a TNC health check
    """
    device = models.ForeignKey(Device,db_column='device',related_name='logins')
    time = models.IntegerField(primary_key=True)
    product = models.ForeignKey(Product,db_column='product')
    count = models.IntegerField(null=True, blank=True)
    count_update = models.IntegerField(null=True, blank=True)
    count_blacklist = models.IntegerField(null=True, blank=True)
    flags = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'device_infos'

class Directory(models.Model):
    """
    Unix-style directory path
    """
    id = models.IntegerField(primary_key=True)
    path = models.TextField()
    

class File(models.Model):
    """
    Filename
    """
    id = models.IntegerField(primary_key=True)
    dir = models.ForeignKey(Directory, db_column='dir', related_name='files')
    name = models.TextField()

    def __unicode__(self):
        return self.name

    def __json__(self):
        return simplejson.dumps({
            'id' : self.id,
            'type' : self.type,
            'path' : self.path,
            })

    class Meta:
        db_table = u'files'

class Algorithm
    """
    A hashing algorithm
    """
    id = models.Integerfield(primary_key=True)
    name = models.TextField(null=False, blank=False)

class FileHash(models.Model):
    """
    SHA-1 or similar filehash
    """
    file = models.ForeignKey(File, db_column='file', related_name='hashes')
    directory = models.ForeignKey(File, db_column='dir', null=True)
    product = models.ForeignKey(Product, db_column='product')
    key = models.IntegerField(null=False, default=0)
    algo = models.ForeignKey(Algorithm, db_column='algo')
    hash = models.TextField()

    class Meta:
        db_table = u'file_hashes'
        unique_together = (("file","product"))

    def __unicode__(self):
        return base64.encodestring(self.hash.__str__())

    def __json__(self):
        return simplejson.dumps({
            'file' : self.file,
            'directory' : self.directory,
            'product' : self.product,
            'key' : self.key,
            'algo' : self.algo,
            'hash' : base64.encodestring(self.hash.__str__()),
            })


class Package(models.Model):
    """
    aptitude Package name
    """
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'packages'

class ProductFile(models.Model):
    """
    Resolving table -> to be dumped?
    """
    product = models.IntegerField()
    file = models.IntegerField()
    measurement = models.IntegerField(null=True, blank=True)
    metadata = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'product_file'

class Version(models.Model):
    """
    Version number string of a package
    """
    id = models.IntegerField(primary_key=True)
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

# The following classes are only stubs. Their purpose is to justify the
# existence of the according database-tables to django
#class Component(models.Model):
#    pass
#    class Meta:
#        db_table = u'component'
#
#class ComponentHash(models.Model):
#    pass
#    class Meta:
#        db_table = u'componenthash'
#
#class Key(models.Model):
#    pass
#    class Meta:
#        db_table = u'key'
#
#class KeyComponent(models.Model):
#    pass
#    class Meta:
#        db_table = u'keycomponent'
