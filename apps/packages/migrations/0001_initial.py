# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import apps.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'packages',
            },
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('release', models.CharField(max_length=255, db_index=True)),
                ('security', models.BooleanField(default=False)),
                ('blacklist', models.BooleanField(default=False)),
                ('time', apps.core.fields.EpochField(default=0)),
                ('package', models.ForeignKey(related_name='versions', db_column='package', to='packages.Package', on_delete=models.CASCADE)),
                ('product', models.ForeignKey(related_name='versions', db_column='product', to='devices.Product', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('package', 'release'),
                'db_table': 'versions',
            },
        ),
        migrations.AlterIndexTogether(
            name='version',
            index_together=set([('package', 'product')]),
        ),
    ]
