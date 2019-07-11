# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('packages', '__first__'),
        ('swid', '0002_rename_to_version_str'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='version',
            field=models.ForeignKey(to='packages.Version', null=True, on_delete=models.CASCADE),
        ),
    ]
