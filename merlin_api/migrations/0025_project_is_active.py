# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-04 00:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merlin_api', '0024_auto_20160504_0001'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
