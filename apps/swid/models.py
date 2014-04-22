# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models


TABLE_PREFIX = 'swid_'


# TODO: After separating the frontend from the strongSwan database, remove the
# custom db_table names.

class Tag(models.Model):
    package_name = models.CharField(max_length=255, db_index=True,
            help_text='The name of the software, e.g. "strongswan"')
    version = models.CharField(max_length=32,
            help_text='The version of the software, e.g. "5.1.2-4.fc19"')
    unique_id = models.CharField(max_length=255, db_index=True,
            help_text='The uniqueID, e.g. "fedora_19-x86_64-strongswan-5.1.2-4.fc19"')
    swid_xml = models.TextField(help_text='The full SWID tag XML')
    files = models.ManyToManyField('tncapp.File', blank=True, verbose_name='list of files')
    sessions = models.ManyToManyField('tncapp.Session', verbose_name='list of sessions')

    class Meta:
        db_table = TABLE_PREFIX + 'tags'

    def __unicode__(self):
        return self.unique_id


class EntityRole(models.Model):
    ROLE_CHOICES = (
        (0, 'Publisher'),
        (1, 'Licensor'),
        (2, 'Tag Creator'),
    )
    tag = models.ForeignKey('Tag')
    entity = models.ForeignKey('Entity')
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES)

    def get_software_id(self):
        """
        Returns the software_id of the tag.
        The software_id consists of the regid and the unique_id.

        Returns:
            software_id (str)

        """
        return '%s_%s' % (self.entity.regid, self.tag.unique_id)

    class Meta:
        db_table = TABLE_PREFIX + 'entityroles'

    def __unicode__(self):
        return '%s as %s' % (self.entity, dict(EntityRole.ROLE_CHOICES)[self.role])


class Entity(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    regid = models.CharField(max_length=255, db_index=True)
    tags = models.ManyToManyField(Tag, through=EntityRole, verbose_name='list of tags')

    class Meta:
        db_table = TABLE_PREFIX + 'entities'
        verbose_name_plural = 'entities'

    def __unicode__(self):
        return self.name
