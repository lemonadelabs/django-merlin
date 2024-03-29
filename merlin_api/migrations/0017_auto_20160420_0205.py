# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 02:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merlin_api', '0016_auto_20160419_2140'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='description',
            field=models.CharField(default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='name',
            field=models.CharField(default='event', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='scenario',
            name='description',
            field=models.CharField(default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='scenario',
            name='name',
            field=models.CharField(default='scenario', max_length=128),
            preserve_default=False,
        ),
    ]
