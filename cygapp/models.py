# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

import base64
import simplejson
from django.db import models

class Device(models.Model):
    """
    Represents and Android Device identified by its AndroidID
    """
    id = models.IntegerField(primary_key=True)
    value = models.TextField()
    class Meta:
        db_table = u'devices'

class DeviceInfo(models.Model):
    """
    Result of a TNC health check
    """
    device = models.ForeignKey(Device,related_name='logins')
    time = models.IntegerField(primary_key=True)
    product = models.ForeignKey(Product)
    count = models.IntegerField(null=True, blank=True)
    count_update = models.IntegerField(null=True, blank=True)
    count_blacklist = models.IntegerField(null=True, blank=True)
    flags = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'device_infos'

class Directory(models.Model):
    id = models.IntegerField(primary_key=True)
    path = models.CharField(null=False, blank=False) #TODO: Sinnvolle max_length?
    

class File(models.Model):
    id = models.IntegerField(primary_key=True)
    dir = models.ForeignKey(Directory, related_name='files')
    name = models.CharField()

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

class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'products'

class FileHash(models.Model):
    file = models.ForeignKey(File, related_name='hashes')
    directory = models.ForeignKey(File, null=True)
    product = models.ForeignKey(Product)
    key = models.IntegerField(null=True, blank=True)
    algo = models.IntegerField()
    hash = models.TextField() # This field type is a guess.

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
    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'packages'

class ProductFile(models.Model):
    product = models.IntegerField()
    file = models.IntegerField()
    measurement = models.IntegerField(null=True, blank=True)
    metadata = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'product_file'

class Version(models.Model):
    id = models.IntegerField(primary_key=True)
    package = models.IntegerField()
    product = models.IntegerField()
    release = models.TextField()
    security = models.IntegerField(null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.release

    class Meta:
        db_table = u'versions'

