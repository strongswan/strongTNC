# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '__first__'),
        ('filesystem', '__first__'),
        ('core', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('regid', models.CharField(max_length=255, db_index=True)),
            ],
            options={
                'ordering': ('regid',),
                'db_table': 'swid_entities',
                'verbose_name_plural': 'entities',
            },
        ),
        migrations.CreateModel(
            name='EntityRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.PositiveSmallIntegerField(choices=[(0, 'aggregator'), (1, 'distributor'), (2, 'licensor'), (3, 'softwareCreator'), (4, 'tagCreator')])),
                ('entity', models.ForeignKey(to='swid.Entity', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'swid_entityroles',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eid', models.PositiveIntegerField()),
                ('epoch', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField()),
                ('device', models.ForeignKey(related_name='events', db_column='device', to='devices.Device', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('device', 'epoch', '-eid'),
                'db_table': 'swid_events',
                'verbose_name_plural': 'events',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('package_name', models.CharField(help_text='The name of the software, e.g. "strongswan"', max_length=255, db_index=True)),
                ('version', models.CharField(help_text='The version of the software, e.g. "5.1.2-4.fc19"', max_length=255)),
                ('unique_id', models.CharField(help_text='The tagId, e.g. "fedora_19-x86_64-strongswan-5.1.2-4.fc19"', max_length=255, db_index=True)),
                ('swid_xml', models.TextField(help_text='The full SWID tag XML')),
                ('software_id', models.CharField(help_text='The Software ID, format: {regid}__{tagId} e.g strongswan.org__fedora_19-x86_64-strongswan-5.1.2-4.fc19', max_length=767, db_index=True)),
                ('files', models.ManyToManyField(to='filesystem.File', verbose_name='list of files', blank=True)),
                ('sessions', models.ManyToManyField(to='core.Session', verbose_name='list of sessions')),
            ],
            options={
                'ordering': ('unique_id',),
                'db_table': 'swid_tags',
            },
        ),
        migrations.CreateModel(
            name='TagEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.PositiveSmallIntegerField(choices=[(1, 'Creation'), (2, 'Deletion'), (3, 'Alteration')])),
                ('record_id', models.PositiveIntegerField()),
                ('source_id', models.PositiveSmallIntegerField()),
                ('event', models.ForeignKey(to='swid.Event', on_delete=models.CASCADE)),
                ('tag', models.ForeignKey(to='swid.Tag', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'swid_tags_events',
                'verbose_name_plural': 'tag events',
            },
        ),
        migrations.CreateModel(
            name='TagStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device', models.ForeignKey(to='devices.Device', on_delete=models.CASCADE)),
                ('first_installed', models.ForeignKey(related_name='tags_first_installed_set', to='swid.Event', null=True, on_delete=models.CASCADE)),
                ('first_seen', models.ForeignKey(related_name='tags_first_seen_set', to='core.Session', on_delete=models.CASCADE)),
                ('last_deleted', models.ForeignKey(related_name='tags_last_deleted_set', to='swid.Event', null=True, on_delete=models.CASCADE)),
                ('last_seen', models.ForeignKey(related_name='tags_last_seen_set', to='core.Session', on_delete=models.CASCADE)),
                ('tag', models.ForeignKey(to='swid.Tag', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('device', 'tag'),
                'verbose_name_plural': 'tag stats',
            },
        ),
        migrations.AddField(
            model_name='event',
            name='tags',
            field=models.ManyToManyField(to='swid.Tag', verbose_name='list of events', through='swid.TagEvent'),
        ),
        migrations.AddField(
            model_name='entityrole',
            name='tag',
            field=models.ForeignKey(to='swid.Tag', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='entity',
            name='tags',
            field=models.ManyToManyField(to='swid.Tag', verbose_name='list of tags', through='swid.EntityRole'),
        ),
        migrations.AlterUniqueTogether(
            name='tagstats',
            unique_together=set([('tag', 'device')]),
        ),
    ]
