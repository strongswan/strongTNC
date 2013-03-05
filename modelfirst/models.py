from django.db import models

class File(models.Model):
    name = models.CharField(max_length=50)
    type = models.BooleanField()

class Product(models.Model):
    name = models.CharField(max_length=200)

class FileHash(models.Model):
    file = models.ForeignKey(File, related_name='filename')
    dir = models.ForeignKey(File, related_name='dirname')
    product = models.ForeignKey(Product)
    algo = models.IntegerField()
    hash = models.TextField()

class ProductFile(models.Model):
    file = models.ForeignKey(File)
    product = models.ForeignKey(Product)
    measurement = models.IntegerField()
    metadata = models.IntegerField()

class Package(models.Model):
    name = models.CharField(max_length=200)

class Version(models.Model):
    package = models.ForeignKey(Package)
    product = models.ForeignKey(Product)
    release = models.IntegerField()
    security = models.BooleanField()
    time = models.DateTimeField()

class Device(models.Model):
    androidID = models.TextField()

class Identity(models.Model):
    somefield = models.BooleanField()

class DeviceInfo(models.Model):
    device = models.ForeignKey(Device)
    product = models.ForeignKey(Product)
    arId = models.ForeignKey(Identity)
    time = models.DateTimeField()
    count = models.IntegerField()
    count_update = models.IntegerField()
    count_blacklist = models.IntegerField()
    flags = models.IntegerField()

