# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import os

from django.db import models


class Directory(models.Model):
    """
    Unix-style directory path.
    """
    path = models.CharField(max_length=255, unique=True)

    class Meta(object):
        db_table = 'directories'
        verbose_name_plural = 'directories'
        ordering = ('path',)

    def __str__(self):
        return self.path

    def list_repr(self):
        """
        String representation in lists
        """
        return self.path


class File(models.Model):
    """
    A file in a directory.
    """
    name = models.CharField(max_length=255, db_index=True)
    directory = models.ForeignKey(Directory, db_column='dir',
                        on_delete=models.CASCADE)

    class Meta(object):
        db_table = 'files'
        ordering = ('directory__path', 'name',)

    def __str__(self):
        if self.directory.path == '/':
            return '/%s' % self.name
        else:
            return '%s/%s' % (self.directory.path, self.name)

    def list_repr(self):
        """
        String representation in lists
        """
        if self.directory.path == '/':
            return '/%s' % self.name
        else:
            return '%s/%s' % (self.directory.path, self.name)

    @classmethod
    def filter(cls, search_term, order_by=Meta.ordering):
        path_part, file_part = os.path.split(search_term)

        files = dirs = None

        # collecting the data from two tables
        if file_part and not path_part:
            files = cls.objects.filter(name__icontains=file_part)
            dirs = Directory.objects.filter(path__icontains=file_part)

        if path_part and not file_part:
            dirs = Directory.objects.filter(path__icontains=path_part)

        if path_part and file_part:
            files = cls.objects.filter(name__icontains=file_part)
            dirs = Directory.objects.filter(path__icontains=search_term)

        resulting_files = []

        # prepare results from collected data
        if files and not dirs:
            resulting_files = files

        if dirs and not files:
            resulting_files = cls.objects.filter(directory__in=dirs)

        if dirs and files:
            resulting_files = files | cls.objects.filter(directory__in=dirs)

        try:
            return resulting_files.order_by(*order_by)
        except AttributeError:  # It's a plain list
            return resulting_files


class Algorithm(models.Model):
    """
    A hashing algorithm.
    """
    name = models.CharField(max_length=20)

    class Meta(object):
        db_table = 'algorithms'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def list_repr(self):
        """
        String representation in lists
        """
        return self.name


class FileHash(models.Model):
    """
    A file hash.
    """
    file = models.ForeignKey(File, db_column='file',
                        on_delete=models.CASCADE)
    version = models.ForeignKey('packages.Version', db_column='version', null=True, blank=True,
                        on_delete=models.CASCADE)
    device = models.ForeignKey('devices.Device', db_column='device', null=True, blank=True,
                        on_delete=models.CASCADE)
    size = models.IntegerField()
    algorithm = models.ForeignKey(Algorithm, db_column='algo',
                        on_delete=models.PROTECT)
    hash = models.CharField(max_length=64, db_column='hash')
    mutable = models.BooleanField(default=False)

    class Meta(object):
        db_table = 'file_hashes'
        verbose_name_plural = 'file hashes'
        ordering = ('file__directory__path', 'file__name',)

    def __str__(self):
        return '%s (%s)' % (self.hash, self.algorithm)

    def list_repr(self):
        """
        String representation in lists
        """
        return '%s (%s)' % (self.hash, self.algorithm)
