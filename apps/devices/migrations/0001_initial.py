# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import apps.core.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=255, db_index=True)),
                ('description', models.TextField(default='', null=True, blank=True)),
                ('created', apps.core.fields.EpochField(null=True, blank=True)),
                ('trusted', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('description',),
                'db_table': 'devices',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('devices', models.ManyToManyField(related_name='groups', db_table='groups_members', to='devices.Device', blank=True)),
                ('parent', models.ForeignKey(related_name='membergroups', db_column='parent', blank=True, to='devices.Group', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'groups',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'products',
            },
        ),
        migrations.AddField(
            model_name='group',
            name='product_defaults',
            field=models.ManyToManyField(related_name='default_groups', to='devices.Product', blank=True),
        ),
        migrations.AddField(
            model_name='device',
            name='product',
            field=models.ForeignKey(related_name='devices', db_column='product', to='devices.Product', on_delete=models.CASCADE),
        ),
    ]
