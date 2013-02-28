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

class ComponentHash(models.Model):
    seq_no = models.IntegerField(primary_key=True)
    component = models.IntegerField()
    key = models.IntegerField()
    pcr = models.IntegerField()
    algo = models.IntegerField()
    hash = models.TextField()
    class Meta:
        db_table = u'component_hashes'

class Component(models.Model):
    id = models.IntegerField(primary_key=True)
    vendor_id = models.IntegerField()
    name = models.IntegerField()
    qualifier = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'components'

class DeviceInfo(models.Model):
    device = models.IntegerField()
    time = models.IntegerField(primary_key=True)
    product = models.IntegerField(null=True, blank=True)
    count = models.IntegerField(null=True, blank=True)
    count_update = models.IntegerField(null=True, blank=True)
    count_blacklist = models.IntegerField(null=True, blank=True)
    flags = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'device_infos'

class Device(models.Model):
    id = models.IntegerField(primary_key=True)
    value = models.TextField()
    class Meta:
        db_table = u'devices'

class FileHash(models.Model):
    file = models.IntegerField()
    directory = models.IntegerField(null=True, primary_key=True, blank=True)
    product = models.IntegerField(primary_key=True)
    key = models.IntegerField(null=True, blank=True)
    algo = models.IntegerField(primary_key=True)
    hash = models.TextField() # This field type is a guess.

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

    class Meta:
        db_table = u'file_hashes'

class File(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.IntegerField()
    path = models.TextField()

    def __unicode__(self):
        return self.path

    def __json__(self):
        return simplejson.dumps({
            'id' : self.id,
            'type' : self.type,
            'path' : self.path,
            })

    class Meta:
        db_table = u'files'

class KeyComponent(models.Model):
    key = models.IntegerField(primary_key=True)
    component = models.IntegerField(primary_key=True)
    depth = models.IntegerField(null=True, blank=True)
    seq_no = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'key_component'

class Key(models.Model):
    id = models.IntegerField(primary_key=True)
    keyid = models.TextField() # This field type is a guess.
    owner = models.TextField()
    class Meta:
        db_table = u'keys'

class Package(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'packages'

class ProductFile(models.Model):
    product = models.IntegerField(primary_key=True)
    file = models.IntegerField(primary_key=True)
    measurement = models.IntegerField(null=True, blank=True)
    metadata = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'product_file'

class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'products'

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

