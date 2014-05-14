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
    files = models.ManyToManyField('filesystem.File', blank=True, verbose_name='list of files')
    sessions = models.ManyToManyField('core.Session', verbose_name='list of sessions')
    software_id = models.TextField(max_length=255, db_index=True,
                                   help_text='The Software ID, format: {regid}_{uniqueID} '
                                             'e.g regid.2004-03.org.strongswan_\
                                             fedora_19-x86_64-strongswan-5.1.2-4.fc19')

    class Meta:
        db_table = TABLE_PREFIX + 'tags'

    def __unicode__(self):
        return self.unique_id

    def list_repr(self):
        return self.unique_id

    @classmethod
    def get_installed_tags_with_time(cls, session):
        """
        Return all measured tags up to the given session with their first
        reported time.

        Only sessions using the same device are included. All tags installed by
        previous sessions are also returned.

        Args:
            session (apps.core.models.Session):
                The session object

        Returns:
            A list of tuples ``(tag, time)``. The ``tag`` is a :class:`Tag`
            instance, the ``time`` is the datetime object when the tag was
            first measured to be installed.

        """
        device_sessions = session.device.sessions.filter(time__lte=session.time).order_by('time')
        tags = {}
        for session in device_sessions.all().prefetch_related('tag_set'):
            for tag in session.tag_set.all():
                if tag not in tags:
                    tags[tag] = session
        return list(tags.items())

    def get_devices_with_reported_session(self):
        devices_dict = {}
        for session in self.sessions.order_by('-time'):
            devices_dict[session.device] = session
        return devices_dict


class EntityRole(models.Model):
    PUBLISHER = 0
    LICENSOR = 1
    TAGCREATOR = 2

    ROLE_CHOICES = (
        (PUBLISHER, 'Publisher'),
        (LICENSOR, 'Licensor'),
        (TAGCREATOR, 'Tag Creator'),
    )

    tag = models.ForeignKey('Tag')
    entity = models.ForeignKey('Entity')
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES)

    class Meta:
        db_table = TABLE_PREFIX + 'entityroles'

    def __unicode__(self):
        return '%s as %s' % (self.entity, dict(EntityRole.ROLE_CHOICES)[self.role])

    def list_repr(self):
        return '%s as %s' % (self.entity, dict(EntityRole.ROLE_CHOICES)[self.role])

    @classmethod
    def xml_attr_to_choice(cls, value):
        if value == 'tagcreator':
            return cls.TAGCREATOR
        elif value == 'licensor':
            return cls.LICENSOR
        elif value == 'publisher':
            return cls.PUBLISHER


class Entity(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    regid = models.CharField(max_length=255, db_index=True)
    tags = models.ManyToManyField(Tag, through=EntityRole, verbose_name='list of tags')

    class Meta:
        db_table = TABLE_PREFIX + 'entities'
        verbose_name_plural = 'entities'

    def __unicode__(self):
        return self.name

    def list_repr(self):
        return self.regid
