# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-05 02:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('merlin_api', '0026_project_scenario'),
    ]

    operations = [
        migrations.RenameField(
            model_name='output',
            old_name='target',
            new_name='minimum',
        ),
    ]