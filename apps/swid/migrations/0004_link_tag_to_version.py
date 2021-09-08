# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def link_version_to_tag(apps, schema_editor):
    Tag = apps.get_model('swid', 'Tag')
    Version = apps.get_model('packages', 'Version')

    for tag in Tag.objects.all():
        try:
            ts = tag.tagstats_set.all()[0]
        except IndexError:
            print('tag %d not migrated' % tag.pk)
            continue
        version = Version.objects.filter(product=ts.device.product,
                                         package__name=ts.tag.package_name, 
                                         release=ts.tag.version_str)
        tag.version = version[0]
        tag.save()
 

class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
        ('packages', '0001_initial'),
        ('swid', '0003_tag_version'),
    ]

    operations = [
        migrations.RunPython(link_version_to_tag),
    ]
