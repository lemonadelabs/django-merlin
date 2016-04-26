# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-25 22:01
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merlin_api', '0017_auto_20160420_0205'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='parameters',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
        ),
        migrations.AlterField(
            model_name='process',
            name='process_class',
            field=models.CharField(max_length=256),
        ),
    ]
