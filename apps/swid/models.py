# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models

from apps.packages.models import Package
from config.settings import XMPP_GRID

TABLE_PREFIX = 'swid_'


# TODO: After separating the frontend from the strongSwan database, remove the
# custom db_table names.


class Tag(models.Model):
    package_name = models.CharField(max_length=255, db_index=True,
                        help_text='The name of the software, e.g. "strongswan"')
    version_str = models.CharField(max_length=255,
                        help_text='The version of the software, e.g. "5.1.2-4.fc19"')
    version = models.ForeignKey('packages.Version', null=True, blank=True,
                        on_delete=models.CASCADE)
    unique_id = models.CharField(max_length=255, db_index=True,
                        help_text='The tagId, e.g. "fedora_19-x86_64-strongswan-5.1.2-4.fc19"')
    swid_xml = models.TextField(help_text='The full SWID tag XML')
    files = models.ManyToManyField('filesystem.File', blank=True, verbose_name='list of files')
    sessions = models.ManyToManyField('core.Session', verbose_name='list of sessions')
    software_id = models.CharField(max_length=767, db_index=True,
                        help_text='The Software ID, format: {regid}__{tagId} '
                                             'e.g strongswan.org__fedora_19-x86_64-strongswan-5.1.2-4.fc19')

    class Meta(object):
        db_table = TABLE_PREFIX + 'tags'
        ordering = ('unique_id',)

    def __str__(self):
        return self.unique_id

    def list_repr(self):
        return self.unique_id

    def json(self):
        j_tag_id = '"tagId": "%s"' % self.unique_id
        j_package_name = '"packageName": "%s"' % self.package_name
        j_version_str = '"versionStr": "%s"' % self.version_str
        j_uri = '"uri": "%s/api/swid-tags/%s/"' % (XMPP_GRID['rest_uri'], self.id)
        j_data = '{%s, %s, %s, %s}' % (j_tag_id, j_package_name, j_version_str, j_uri)
        return j_data

    @classmethod
    def get_installed_tags_with_time(cls, session):
        """
        Return all measured tags up to the given session with their first
        reported  and last reported time.

        Only sessions using the same device are included. All tags installed by
        previous sessions are also returned.

        Args:
            session (apps.core.models.Session):
                The session object

        Returns:
            A list of TagStat objects, containing first_seen and last_seen sessions
            as well as a reference to the tag instance.

        """
        tag_pks = session.tag_set.values_list('pk', flat=True)
        tag_stats = TagStats.objects.filter(tag__in=tag_pks, device=session.device_id) \
            .select_related('last_seen', 'first_seen', 'tag').defer('tag__swid_xml')
        return tag_stats

    def get_matching_packages(self):
        return Package.objects.filter(name=self.package_name)


class TagStats(models.Model):
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE)
    first_seen = models.ForeignKey('core.Session', on_delete=models.CASCADE,
                        related_name='tags_first_seen_set')
    last_seen = models.ForeignKey('core.Session', on_delete=models.CASCADE,
                        related_name='tags_last_seen_set')
    first_installed = models.ForeignKey('Event', null=True, on_delete=models.CASCADE,
                        related_name='tags_first_installed_set')
    last_deleted = models.ForeignKey('Event', null=True, on_delete=models.CASCADE,
                        related_name='tags_last_deleted_set')

    class Meta(object):
        unique_together = ('tag', 'device')
        verbose_name_plural = 'tag stats'
        ordering = ('device', 'tag')


class EntityRole(models.Model):
    AGGREGATOR = 0
    DISTRIBUTOR = 1
    LICENSOR = 2
    SOFTWARE_CREATOR = 3
    TAG_CREATOR = 4

    ROLE_CHOICES = (
        (AGGREGATOR, 'aggregator'),
        (DISTRIBUTOR, 'distributor'),
        (LICENSOR, 'licensor'),
        (SOFTWARE_CREATOR, 'softwareCreator'),
        (TAG_CREATOR, 'tagCreator'),
    )

    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES)

    class Meta(object):
        db_table = TABLE_PREFIX + 'entityroles'

    def __str__(self):
        return '%s as %s' % (self.entity, dict(EntityRole.ROLE_CHOICES)[self.role])

    def list_repr(self):
        return '%s as %s' % (self.entity, dict(EntityRole.ROLE_CHOICES)[self.role])

    @classmethod
    def xml_attr_to_choice(cls, value):
        if value == 'tagCreator':
            return cls.TAG_CREATOR
        elif value == 'tagcreator':
            # Support of SWID draft standard
            return cls.TAG_CREATOR
        elif value == 'softwareCreator':
            return cls.SOFTWARE_CREATOR
        elif value == 'licensor':
            return cls.LICENSOR
        elif value == 'distributor':
            return cls.DISTRIBUTOR
        elif value == 'aggregator':
            return cls.AGGREGATOR
        else:
            raise ValueError('Unknown role: %s' % value)


class Entity(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    regid = models.CharField(max_length=255, db_index=True)
    tags = models.ManyToManyField(Tag, through=EntityRole, verbose_name='list of tags')

    class Meta(object):
        db_table = TABLE_PREFIX + 'entities'
        verbose_name_plural = 'entities'
        ordering = ('regid',)

    def __str__(self):
        return self.name

    def list_repr(self):
        return self.regid


class TagEvent(models.Model):
    CREATION = 1
    DELETION = 2
    ALTERATION = 3

    ACTION_CHOICES = (
        (CREATION, 'Creation'),
        (DELETION, 'Deletion'),
        (ALTERATION, 'Alteration'),
    )

    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    action = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)
    record_id = models.PositiveIntegerField()
    source_id = models.PositiveSmallIntegerField()

    class Meta(object):
        db_table = TABLE_PREFIX + 'tags_events'
        verbose_name_plural = 'tag events'

    def __str__(self):
        return ' %s in %s' % (self.tag, self.event)

    def list_repr(self):
        return '%s in %s' % (self.tag, self.event)


class Event(models.Model):
    device = models.ForeignKey('devices.Device', db_column='device', db_index=True,
                        on_delete=models.CASCADE, related_name='events')
    eid = models.PositiveIntegerField()
    epoch = models.PositiveIntegerField()
    timestamp = models.DateTimeField()
    tags = models.ManyToManyField(Tag, through=TagEvent, verbose_name='list of events')

    class Meta(object):
        db_table = TABLE_PREFIX + 'events'
        verbose_name_plural = 'events'
        ordering = ('device', 'epoch', '-eid')

    def __str__(self):
        return 'EID %s of %s' % (self.eid, self.device)

    def list_repr(self):
        return 'EID %s of %s' % (self.eid, self.devices)
