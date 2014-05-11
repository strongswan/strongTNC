# -*- coding: utf-8 -*-
"""
Script to create a db with test data

Usage:
$ ./manage.py shell
>>> execfile('tests/create_test_db.py')

"""
from __future__ import print_function, division, absolute_import, unicode_literals

from apps.swid import utils
from apps.swid.models import Tag, EntityRole, Entity

from apps.devices.models import Device

# TRUNCATE SWID TABLES

Tag.files.through.objects.all().delete()
Tag.sessions.through.objects.all().delete()
Tag.objects.all().delete()

EntityRole.objects.all().delete()
Entity.objects.all().delete()


# IMPORT SWID TAGS

filename = "tests/test_tags/ubuntu_full_swid.txt"
with open(filename, 'r') as f:
    for line in f:
        tag_xml = line.strip().decode('utf8')
        tag = utils.process_swid_tag(tag_xml)
        print('Processed {0}'.format(tag))


# WIRE UP SOME SESSIONS WITH TAGS

nexus_prime = Device.objects.get(pk=2)
lenovo_twist = Device.objects.get(pk=1)
sessions_prime = nexus_prime.sessions.order_by('-time')[:5]
sessions_twist = lenovo_twist.sessions.order_by('-time')[:5]

tag_sets = [
    Tag.objects.filter(id__in=range(100)),
    Tag.objects.filter(id__in=range(45)),
    Tag.objects.filter(id__in=range(50)),
    Tag.objects.filter(id__in=range(25)),
    Tag.objects.filter(id__in=range(10))
]

for idx, session in enumerate(sessions_prime):
    session.tag_set.add(*tag_sets[idx])
    sessions_twist[idx].tag_set.add(*tag_sets[idx])